from typing import List, Callable, Tuple, Dict, Iterable, Iterator, Union, Any
from typing import Optional, TYPE_CHECKING
from pathlib import Path
from timeit import default_timer as timer
from thinc.api import Optimizer, Config, constant, fix_random_seed, set_gpu_allocator
import random
import tqdm
from wasabi import Printer

from .example import Example
from ..schemas import ConfigSchemaTraining
from ..errors import Errors
from ..util import resolve_dot_names, registry

if TYPE_CHECKING:
    from ..language import Language  # noqa: F401


def train(
    nlp: "Language",
    output_path: Optional[Path] = None,
    *,
    use_gpu: int = -1,
    silent: bool = False,
) -> None:
    """Train a pipeline.

    nlp (Language): The initialized nlp object with the full config.
    output_path (Path): Optional output path to save trained model to.
    use_gpu (int): Whether to train on GPU. Make sure to call require_gpu
        before calling this function.
    silent (bool): Whether to pretty-print outputs.
    RETURNS (Path / None): The path to the final exported model.
    """
    msg = Printer(no_print=silent)
    # Create iterator, which yields out info after each optimization step.
    config = nlp.config.interpolate()
    if config["training"]["seed"] is not None:
        fix_random_seed(config["training"]["seed"])
    allocator = config["training"]["gpu_allocator"]
    if use_gpu >= 0 and allocator:
        set_gpu_allocator(allocator)
    T = registry.resolve(config["training"], schema=ConfigSchemaTraining)
    dot_names = [T["train_corpus"], T["dev_corpus"]]
    train_corpus, dev_corpus = resolve_dot_names(config, dot_names)
    optimizer = T["optimizer"]
    score_weights = T["score_weights"]
    batcher = T["batcher"]
    train_logger = T["logger"]
    before_to_disk = create_before_to_disk_callback(T["before_to_disk"])
    # Components that shouldn't be updated during training
    frozen_components = T["frozen_components"]
    # Create iterator, which yields out info after each optimization step.
    training_step_iterator = train_while_improving(
        nlp,
        optimizer,
        create_train_batches(train_corpus(nlp), batcher, T["max_epochs"]),
        create_evaluation_callback(nlp, dev_corpus, score_weights),
        dropout=T["dropout"],
        accumulate_gradient=T["accumulate_gradient"],
        patience=T["patience"],
        max_steps=T["max_steps"],
        eval_frequency=T["eval_frequency"],
        exclude=frozen_components,
    )
    msg.info(f"Pipeline: {nlp.pipe_names}")
    if frozen_components:
        msg.info(f"Frozen components: {frozen_components}")
    msg.info(f"Initial learn rate: {optimizer.learn_rate}")
    with nlp.select_pipes(disable=frozen_components):
        print_row, finalize_logger = train_logger(nlp)
    try:
        progress = tqdm.tqdm(total=T["eval_frequency"], leave=False)
        progress.set_description(f"Epoch 1")
        for batch, info, is_best_checkpoint in training_step_iterator:
            progress.update(1)
            if is_best_checkpoint is not None:
                progress.close()
                print_row(info)
                if is_best_checkpoint and output_path is not None:
                    with nlp.select_pipes(disable=frozen_components):
                        update_meta(T, nlp, info)
                    with nlp.use_params(optimizer.averages):
                        nlp = before_to_disk(nlp)
                        nlp.to_disk(output_path / "model-best")
                progress = tqdm.tqdm(total=T["eval_frequency"], leave=False)
                progress.set_description(f"Epoch {info['epoch']}")
    except Exception as e:
        finalize_logger()
        if output_path is not None:
            # We don't want to swallow the traceback if we don't have a
            # specific error.
            msg.warn(
                f"Aborting and saving the final best model. "
                f"Encountered exception: {str(e)}"
            )
            nlp = before_to_disk(nlp)
            nlp.to_disk(output_path / "model-final")
        raise e
    finally:
        finalize_logger()
        if output_path is not None:
            final_model_path = output_path / "model-final"
            if optimizer.averages:
                with nlp.use_params(optimizer.averages):
                    nlp.to_disk(final_model_path)
            else:
                nlp.to_disk(final_model_path)
            msg.good(f"Saved pipeline to output directory", final_model_path)


def train_while_improving(
    nlp: "Language",
    optimizer: Optimizer,
    train_data,
    evaluate,
    *,
    dropout: float,
    eval_frequency: int,
    accumulate_gradient: int,
    patience: int,
    max_steps: int,
    exclude: List[str],
):
    """Train until an evaluation stops improving. Works as a generator,
    with each iteration yielding a tuple `(batch, info, is_best_checkpoint)`,
    where info is a dict, and is_best_checkpoint is in [True, False, None] --
    None indicating that the iteration was not evaluated as a checkpoint.
    The evaluation is conducted by calling the evaluate callback.

    Positional arguments:
        nlp: The spaCy pipeline to evaluate.
        optimizer: The optimizer callable.
        train_data (Iterable[Batch]): A generator of batches, with the training
            data. Each batch should be a Sized[Tuple[Input, Annot]]. The training
            data iterable needs to take care of iterating over the epochs and
            shuffling.
        evaluate (Callable[[], Tuple[float, Any]]): A callback to perform evaluation.
            The callback should take no arguments and return a tuple
            `(main_score, other_scores)`. The main_score should be a float where
            higher is better. other_scores can be any object.

    Every iteration, the function yields out a tuple with:

    * batch: A list of Example objects.
    * info: A dict with various information about the last update (see below).
    * is_best_checkpoint: A value in None, False, True, indicating whether this
        was the best evaluation so far. You should use this to save the model
        checkpoints during training. If None, evaluation was not conducted on
        that iteration. False means evaluation was conducted, but a previous
        evaluation was better.

    The info dict provides the following information:

        epoch (int): How many passes over the data have been completed.
        step (int): How many steps have been completed.
        score (float): The main score from the last evaluation.
        other_scores: : The other scores from the last evaluation.
        losses: The accumulated losses throughout training.
        checkpoints: A list of previous results, where each result is a
            (score, step, epoch) tuple.
    """
    if isinstance(dropout, float):
        dropouts = constant(dropout)
    else:
        dropouts = dropout
    results = []
    losses = {}
    words_seen = 0
    start_time = timer()
    for step, (epoch, batch) in enumerate(train_data):
        dropout = next(dropouts)
        for subbatch in subdivide_batch(batch, accumulate_gradient):
            nlp.update(
                subbatch, drop=dropout, losses=losses, sgd=False, exclude=exclude
            )
        # TODO: refactor this so we don't have to run it separately in here
        for name, proc in nlp.pipeline:
            if (
                name not in exclude
                and hasattr(proc, "model")
                and proc.model not in (True, False, None)
            ):
                proc.model.finish_update(optimizer)
        optimizer.step_schedules()
        if not (step % eval_frequency):
            if optimizer.averages:
                with nlp.use_params(optimizer.averages):
                    score, other_scores = evaluate()
            else:
                score, other_scores = evaluate()
            results.append((score, step))
            is_best_checkpoint = score == max(results)[0]
        else:
            score, other_scores = (None, None)
            is_best_checkpoint = None
        words_seen += sum(len(eg) for eg in batch)
        info = {
            "epoch": epoch,
            "step": step,
            "score": score,
            "other_scores": other_scores,
            "losses": losses,
            "checkpoints": results,
            "seconds": int(timer() - start_time),
            "words": words_seen,
        }
        yield batch, info, is_best_checkpoint
        if is_best_checkpoint is not None:
            losses = {}
        # Stop if no improvement in `patience` updates (if specified)
        best_score, best_step = max(results)
        if patience and (step - best_step) >= patience:
            break
        # Stop if we've exhausted our max steps (if specified)
        if max_steps and step >= max_steps:
            break


def subdivide_batch(batch, accumulate_gradient):
    batch = list(batch)
    batch.sort(key=lambda eg: len(eg.predicted))
    sub_len = len(batch) // accumulate_gradient
    start = 0
    for i in range(accumulate_gradient):
        subbatch = batch[start : start + sub_len]
        if subbatch:
            yield subbatch
        start += len(subbatch)
    subbatch = batch[start:]
    if subbatch:
        yield subbatch


def create_evaluation_callback(
    nlp: "Language", dev_corpus: Callable, weights: Dict[str, float]
) -> Callable[[], Tuple[float, Dict[str, float]]]:
    weights = {key: value for key, value in weights.items() if value is not None}

    def evaluate() -> Tuple[float, Dict[str, float]]:
        dev_examples = list(dev_corpus(nlp))
        scores = nlp.evaluate(dev_examples)
        # Calculate a weighted sum based on score_weights for the main score.
        # We can only consider scores that are ints/floats, not dicts like
        # entity scores per type etc.
        for key, value in scores.items():
            if key in weights and not isinstance(value, (int, float)):
                raise ValueError(Errors.E915.format(name=key, score_type=type(value)))
        try:
            weighted_score = sum(
                scores.get(s, 0.0) * weights.get(s, 0.0) for s in weights
            )
        except KeyError as e:
            keys = list(scores.keys())
            err = Errors.E983.format(dict="score_weights", key=str(e), keys=keys)
            raise KeyError(err) from None
        return weighted_score, scores

    return evaluate


def create_train_batches(
    iterator: Iterator[Example],
    batcher: Callable[[Iterable[Example]], Iterable[Example]],
    max_epochs: int,
):
    epoch = 0
    examples = list(iterator)
    if not examples:
        # Raise error if no data
        raise ValueError(Errors.E986)
    while max_epochs < 1 or epoch != max_epochs:
        random.shuffle(examples)
        for batch in batcher(examples):
            yield epoch, batch
        epoch += 1


def update_meta(
    training: Union[Dict[str, Any], Config], nlp: "Language", info: Dict[str, Any]
) -> None:
    nlp.meta["performance"] = {}
    for metric in training["score_weights"]:
        if metric is not None:
            nlp.meta["performance"][metric] = info["other_scores"].get(metric, 0.0)
    for pipe_name in nlp.pipe_names:
        nlp.meta["performance"][f"{pipe_name}_loss"] = info["losses"][pipe_name]


def create_before_to_disk_callback(
    callback: Optional[Callable[["Language"], "Language"]]
) -> Callable[["Language"], "Language"]:
    from ..language import Language  # noqa: F811

    def before_to_disk(nlp: Language) -> Language:
        if not callback:
            return nlp
        modified_nlp = callback(nlp)
        if not isinstance(modified_nlp, Language):
            err = Errors.E914.format(name="before_to_disk", value=type(modified_nlp))
            raise ValueError(err)
        return modified_nlp

    return before_to_disk
