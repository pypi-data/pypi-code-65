import logging
from datetime import datetime
from typing import List, Optional
import math

import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.layers import Input, Dense, TimeDistributed, Dropout, Lambda, BatchNormalization, Activation
from tensorflow.keras.models import Model
from tensorflow.keras import regularizers
from transformers import TFDistilBertModel, DistilBertTokenizerFast

from bavard_nlu.data_preprocessing.data_preprocessor import DataPreprocessor
from bavard_nlu.data_preprocessing.prediction_input import PredictionInput
from bavard_nlu.utils import assert_all_not_none

logging.getLogger().setLevel(logging.DEBUG)


class NLUModel:

    min_num_examples = 5
    min_batch_size = 4
    min_train_size_for_validation = 250
    max_val_size = 10000
    default_val_ratio = 0.2
    default_num_epochs = 30  # used when no early stopping takes place
    max_epochs = 1000
    # Format: `(min_examples, batch_size)`.
    # Based on the function `(n/50)+4`
    batch_size_lower_bounds = [
        (min_num_examples, min_batch_size),
        (200, 8),
        (600, 16),
        (1400, 32),
        (3000, 64)
    ]
    embedder_name = 'distilbert-base-multilingual-cased'
    hpnames = [
        "hidden_size",
        "dropout",
        "l2_regularization",
        "hidden_activation",
        "n_hidden_layers",
        "fine_tune_embedder",
        "learning_rate",
        "batch_size",
        "epochs",
    ]

    def __init__(
        self,
        agent_data: dict,
        max_seq_len: int,
        saved_model_dir: Optional[str] = None,
        load_model: bool = False,
        verbose: bool = False,
        *,
        hidden_size: int = 256,
        dropout: float = 0.1,
        l2_regularization: float = 0.0,
        hidden_activation: str = "relu",
        n_hidden_layers: int = 0,
        fine_tune_embedder: bool = True,
        learning_rate: float = 5e-5,
        batch_size: int = 4,
        epochs: int = 30,
    ):
        self.agent_data = agent_data
        intents = self.agent_data['nluData']['intents']
        tag_types = self.agent_data['nluData']['tagTypes']

        self.intents = sorted(intents)
        self.tag_types = sorted(tag_types)
        self.max_seq_len = max_seq_len
        self.save_model_dir = saved_model_dir
        self.verbose = verbose

        # intents encoder
        self.intents_encoder = LabelEncoder()
        self.intents_encoder.fit(self.intents)

        # tags encoder
        tag_set = {'[CLS]', '[SEP]', 'O'}
        for tag_type in tag_types:
            tag_set.add(f'B-{tag_type}')
            tag_set.add(f'I-{tag_type}')
        self.tag_encoder = LabelEncoder()
        self.tag_encoder.fit(list(tag_set))

        # tag and intent sizes
        self.n_tags = len(tag_set)
        self.n_intents = len(intents)

        self.model = None
        self.tokenizer = None
        
        # Set hyperparameters
        self.hidden_size = hidden_size
        self.dropout = dropout
        self.l2_regularization = l2_regularization
        self.hidden_activation = hidden_activation
        self.n_hidden_layers = n_hidden_layers
        self.fine_tune_embedder = fine_tune_embedder
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.epochs = epochs

        if load_model:
            self.model = tf.keras.models.load_model(saved_model_dir)
            self._compile_model()

    @staticmethod
    def get_embedder(*, trainable: bool = False) -> tf.keras.Model:
        # TODO: Shouldn't have to access the underlying `.distilbert` layer once
        # https://github.com/huggingface/transformers/issues/3627 is resolved.
        embedder = TFDistilBertModel.from_pretrained(NLUModel.embedder_name).distilbert
        embedder.trainable = trainable
        return embedder

    @staticmethod
    def get_tokenizer() -> DistilBertTokenizerFast:
        return DistilBertTokenizerFast.from_pretrained(NLUModel.embedder_name)
    
    def get_params(self) -> dict:
        """
        Get a copy of the model's hyperparameters as a dictionary.
        """
        return {name: getattr(self, name) for name in self.hpnames}
    
    def set_params(self, **params) -> None:
        """
        Sets the hyperparameters found in `**params`.
        """
        for name, value in params.items():
            if name in self.hpnames:
                setattr(self, name, value)
            else:
                raise ValueError(f"{name} is not a known hyperparameter")

    def build_and_compile_model(self):
        embedder = self.get_embedder(trainable=self.fine_tune_embedder)
        self.tokenizer = self.get_tokenizer()

        in_id = Input(shape=(self.max_seq_len,), name='input_ids', dtype=tf.int32)
        in_mask = Input(shape=(self.max_seq_len,), name='input_mask', dtype=tf.int32)
        word_start_mask = Input(shape=(self.max_seq_len,), name='word_start_mask', dtype=tf.float32)
        embedder_inputs = [in_id, in_mask]
        all_inputs = [in_id, in_mask, word_start_mask]

        # The output of the pretrained base model.
        token_embeddings = embedder(embedder_inputs)[0]
        pooled_embedding = token_embeddings[:, 0]

        # A network for intent classification.
        
        intent_out = pooled_embedding
        for _ in range(self.n_hidden_layers):
            intent_out = Dropout(rate=self.dropout)(intent_out)
            intent_out = Dense(
                self.hidden_size,
                activation=None,
                kernel_regularizer=regularizers.L2(self.l2_regularization),
            )(intent_out)
            intent_out = BatchNormalization()(intent_out)
            intent_out = Activation(self.hidden_activation)(intent_out)

        intent_out = Dense(self.n_intents, activation='softmax', name='intent')(intent_out)

        # Another network for NER.

        tags_out = token_embeddings
        for _ in range(self.n_hidden_layers):
            tags_out = Dropout(rate=self.dropout)(tags_out)
            tags_out = TimeDistributed(Dense(
                self.hidden_size,
                activation=self.hidden_activation,
                kernel_regularizer=regularizers.L2(self.l2_regularization),
            ))(tags_out)
            tags_out = BatchNormalization()(tags_out)
            tags_out = Activation(self.hidden_activation)(tags_out)

        tags_out = TimeDistributed(Dense(self.n_tags, activation='softmax'))(tags_out)
        tags_out = Lambda(lambda x: x, name='tags')(tags_out)
        # tags_out = Multiply(name='tagger')([tags_out, word_start_mask])

        self.model = Model(inputs=all_inputs, outputs=[intent_out, tags_out])
        self._compile_model()

    def _compile_model(self):
        optimizer = tf.keras.optimizers.Adam(self.learning_rate)
        losses = {
            'tags': 'sparse_categorical_crossentropy',
            'intent': 'sparse_categorical_crossentropy'
        }
        loss_weights = {'tags': 3.0, 'intent': 1.0}
        metrics = {'intent': 'acc', 'tags': 'acc'}
        self.model.compile(optimizer=optimizer, loss=losses, loss_weights=loss_weights, metrics=metrics)
        if self.verbose:
            self.model.summary()

    def get_tags_output_mask(self, word_start_mask):
        word_start_mask = np.expand_dims(word_start_mask, axis=2)  # n x seq_len x 1
        tags_output_mask = np.tile(word_start_mask, (1, 1, self.n_tags))  # n x seq_len x n_tags
        return tags_output_mask

    def train(self, batch_size: int = None, epochs: int = None, auto: bool = False):
        """
        Processes the agent data into training data, and trains the model.
        If `auto==True`, hyperparameters are determined automatically.
        """
        if not auto:
            if batch_size is not None:
                self.batch_size = batch_size
            if epochs is not None:
                self.epochs = epochs

        dataset = DataPreprocessor.preprocess(self.agent_data, self.tokenizer).to_dataset(self.max_seq_len)
        train_data, val_data, hparams, callbacks = self.get_training_setup(auto, dataset, self.get_params())
        self.set_params(**hparams)

        self._fit(train_data, val_data, callbacks)
        
        if self.save_model_dir is not None:
            # Save the model's state, so it can be deployed and used.
            self.model.save(self.save_model_dir, save_format="tf")
    
    def _fit(
        self,
        train_data: tf.data.Dataset,
        val_data: tf.data.Dataset = None,
        callbacks: list = None,
        tensorboard: bool = True
    ) -> None:
        """
        Fits the model on `train_data`, using optional `val_data` for validation.
        `train_data` and `val_data` should be passed in unbatched.
        """
        if callbacks is None:
            callbacks = []

        if val_data:
            val_data = val_data.batch(self.batch_size)

        if tensorboard:
            logdir = "logs/" + datetime.now().strftime("%Y%m%d-%H%M%S")
            callbacks.append(tf.keras.callbacks.TensorBoard(log_dir=logdir))

        n_train = sum(1 for _ in train_data)

        self.model.fit(
            train_data.batch(self.batch_size),
            epochs=self.epochs,
            steps_per_epoch=self._get_steps_per_epoch(n_train, self.batch_size),
            validation_data=val_data,
            use_multiprocessing=True,
            callbacks=callbacks
        )
    
    def evaluate(
        self,
        batch_size: int = None,
        epochs: int = None,
        auto: bool = False,
        test_ratio: float = None
    ) -> tuple:
        """
        Evaluates the model's training set and test set performance
        on it's agent's data.

        Returns
        -------
        training_performance : dict
            The metrics from evaluating the fitted model on the training set.
        test_performance : dict
            The metrics from evaluating the fitted model on the test set.
        """
        if test_ratio is None:
            test_ratio = self.default_val_ratio
            
        dataset, test_data = DataPreprocessor.preprocess(self.agent_data, self.tokenizer).to_dataset_split(self.max_seq_len, test_ratio)
        train_data, val_data, hparams, callbacks = self.get_training_setup(auto, dataset, self.get_params())
        self.set_params(**hparams)

        self._fit(train_data, val_data, callbacks, False)

        train_performance = self.model.evaluate(train_data.batch(self.batch_size), return_dict=True)
        test_performance = self.model.evaluate(test_data.batch(self.batch_size), return_dict=True)

        return train_performance, test_performance
    
    @staticmethod
    def get_training_setup(auto: bool, dataset: tf.data.Dataset, hparams: dict) -> tuple:
        """
        Determines and creates the training set up to use, including hyperparameter
        settings and train/validation splits. Supports `auto` mode and non-auto mode.

        Parameters
        ----------
        auto : bool
            If `True`, hyperparameters and splits are determined automatically. If `False`,
            the hyperparameters present in `hparams` will be used, and no split will occur.
        dataset : tf.data.Dataset
            The full training dataset used to create the train/validatino split.
        hparams : dict
            The hyperparameter values passed in by the user.
        
        Returns
        -------
        train_data : tf.data.Dataset
            The training portion of the dataset split.
        val_data : tf.data.Dataset
            The validatin portion of the dataset split. Set to `None` if
            there is no validation data.
        hparams : dict
            The updated hyperparameter settings to use when training.
        callbacks : list
            Any callback functions the model should be sure to use when
            fitting.
        """
        n = sum(1 for _ in dataset)
        NLUModel._assert_min_dataset_size(n)
        dataset = dataset.shuffle(buffer_size=1000, seed=0)

        if not auto:
            # Use the user-provided settings.

            # Values must be passed in for the hyperparameters when auto mode is off.
            assert_all_not_none(**hparams)
            logging.info(f'Training example count: {n}')
            return dataset, None, hparams, []
        
        # Automatically determine the training set up using some
        # heuristics.

        if n < NLUModel.min_train_size_for_validation:
            # No validation set will be used -- the dataset is too small.

            hparams["batch_size"] = NLUModel._determine_batch_size(n)
            hparams["epochs"] = NLUModel.default_num_epochs
            logging.info(f'Training example count: {n}')
            return dataset, None, hparams, []
        
        # A validation set and early stopping will be used.

        n_val = NLUModel._get_val_size(n)
        n_train = n - n_val

        hparams["batch_size"] = NLUModel._determine_batch_size(n_train)
        # Since we're using early stopping, the `epochs` hparam essentially becomes a
        # max epochs hparam.
        hparams["epochs"] = NLUModel.max_epochs
        
        val_data = dataset.take(n_val)
        train_data = dataset.skip(n_val)

        # Use early stopping.
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor="val_loss",
                min_delta=1e-5,
                patience=3
            )
        ]

        logging.info(f'Training example count: {n_train}')
        logging.info(f'Validation example count: {n_val}')
        return train_data, val_data, hparams, callbacks
    
    @staticmethod
    def _get_steps_per_epoch(n: int, b: int) -> int:
        """
        Returns the number of steps per epoch a model should take
        while training, given `n`, the number of examples in the training set,
        and `b`, the batch size.
        """
        return math.ceil(n / b)
    
    @staticmethod
    def _determine_batch_size(n: int) -> int:
        """
        Uses a heuristic to determine a good batch size to use,
        given dataset size `n` (uses a linear function of `n`, rounding
        to a power of 2).
        """
        NLUModel._assert_min_dataset_size(n)
        batch_size = NLUModel.min_batch_size
        for lower_bound, b in NLUModel.batch_size_lower_bounds:
            if n >= lower_bound:
                batch_size = b
        return batch_size
    
    @staticmethod
    def _assert_min_dataset_size(n: int) -> None:
        if n < NLUModel.min_num_examples:
            raise Exception(
                f"Too few examples to train, must be at least {NLUModel.min_num_examples}"
            )
    
    @staticmethod
    def _get_val_size(n: int, val_ratio: float = None) -> int:
        if val_ratio is None:
            val_ratio = NLUModel.default_val_ratio
        return min(int(n * NLUModel.default_val_ratio), NLUModel.max_val_size)

    def predict(self, text: str, tokenizer: DistilBertTokenizerFast):
        text = text.lower()
        raw_input = PredictionInput(text=text, max_seq_len=self.max_seq_len, tokenizer=tokenizer)
        x = raw_input.to_model_input()
        prediction = self.model.predict(x=x)
        return prediction

    def decode_intent(self, raw_intent_prediction: np.ndarray) -> dict:
        intent_max = np.argmax(raw_intent_prediction)
        confidence = np.max(raw_intent_prediction)
        decoded_intent = self.intents_encoder.inverse_transform([intent_max])[0]
        return {"value": decoded_intent, "confidence": confidence}

    def decode_tags(self, raw_tag_predictions: np.ndarray, text: str, word_start_mask: List[int]):
        raw_tag_predictions = np.squeeze(raw_tag_predictions)
        assert raw_tag_predictions.shape[0] == len(word_start_mask)
        decoded_tags = []
        for i, e in enumerate(word_start_mask):
            if e == 1:
                predicted_tag_idx = np.argmax(raw_tag_predictions[i])
                predicted_tag = self.tag_encoder.inverse_transform([predicted_tag_idx])[0]
                decoded_tags.append(predicted_tag)

        words = text.split()

        result = []
        current_tag_words = []
        current_tag_type = None
        for i, tag in enumerate(decoded_tags):
            if tag == 'O':
                if current_tag_words and current_tag_type:
                    result.append({
                        'tag_type': current_tag_type,
                        'value': ' '.join(current_tag_words),
                    })

                current_tag_type = None
                current_tag_words = []
                continue

            if tag.startswith('B-'):
                if current_tag_words and current_tag_type:
                    result.append({
                        'tag_type': current_tag_type,
                        'value': ' '.join(current_tag_words),
                    })

                current_tag_words = [words[i]]
                current_tag_type = tag[2:]
            elif tag.startswith('I-'):
                current_tag_words.append(words[i])

        if current_tag_words and current_tag_type:
            result.append({
                'tag_type': current_tag_type,
                'value': ' '.join(current_tag_words),
            })

        return result
