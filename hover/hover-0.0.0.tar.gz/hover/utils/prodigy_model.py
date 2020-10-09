"""
Submodule for a Prodigy-compliant transfer learning model along with a Prodigy recipe to use it.
"""

from __future__ import unicode_literals

import prodigy
from prodigy.components.loaders import JSONL
from prodigy.components.sorters import (
    prefer_uncertain,
    prefer_low_scores,
    prefer_high_scores,
)
import random
from copy import deepcopy
import torch
import torch.nn.functional as F
from datetime import datetime
from hover.utils.torch_helper import vector_dataloader, one_hot, label_smoothing
from hover.evaluation import classification_accuracy
from hover.proposal import unit_scale_entropy
from hover.module_params import PRODIGY_KEY_TRANSFORM_PREFIX, default_logger
from sklearn.metrics import confusion_matrix
from snorkel.classification import cross_entropy_with_probs
import numpy as np


def create_text_vector_net_from_module(specific_class, model_module_name, labels):
    """
    Create a TextVectorNet model, or of its child class.
    :param specific_class: TextVectorNet or its child class.
    :type specific_class: class
    :param model_module_name: path to a local Python module in the working directory whose __init__.py file contains a get_text_to_vec() callable, get_architecture() callable, and a get_state_dict_path() callable.
    :type model_module_name: str
    :param labels: the classification labels, e.g. ["POSITIVE", "NEGATIVE"].
    :type labels: list of str
    """
    from importlib import import_module

    model_module = import_module(model_module_name)

    # Load the model by retrieving the text-to-vec function, architecture, and state dict
    model = specific_class(
        model_module.get_text_to_vec(),
        model_module.get_architecture(),
        model_module.get_state_dict_path(),
        labels,
    )

    return model


class TextVectorNet(object):
    """Simple transfer learning model: a user-supplied text vectorizer followed by a neural net.
    This is a parent class whose children may use different training schemes.
    Intended to support both active learning with Prodigy and any sophisticated training method.
    Please refer to hover.utils.torch_helper.VectorDataset and vector_dataloader for more info.
    """

    def __init__(self, text_to_vec, architecture, state_dict_path, labels):
        """
        :param text_to_vec: a function that converts any string to a NumPy 1-D array.
        :type text_to_vec: callable
        :param architecture: a Torch.nn.Module child class to be instantiated into a neural net.
        :type architecture: child class of Torch.nn.Module
        :param state_dict_path: path to a PyTorch state dict that matches the architecture.
        :type state_dict_path: str
        :param labels: the classification labels, e.g. ["POSITIVE", "NEGATIVE"].
        :type labels: list of str
        """

        # create a logger for debug information handling
        self.logger = default_logger()

        # set up label conversion
        self.label_encoder = {_label: i for i, _label in enumerate(labels)}
        self.label_decoder = {i: _label for i, _label in enumerate(labels)}
        self.num_classes = len(self.label_encoder)

        # set up vectorizer and the neural network with appropriate dimensions
        self.vectorizer = text_to_vec
        vec_dim = self.vectorizer("").shape[0]
        self.nn = architecture(vec_dim, self.num_classes)

        # if a state dict exists, load it and create a backup copy
        import os

        if os.path.isfile(state_dict_path):
            from shutil import copyfile

            self.nn.load_state_dict(torch.load(state_dict_path))
            state_dict_backup_path = (
                f"{state_dict_path}.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            copyfile(state_dict_path, state_dict_backup_path)

        # set a path to store updated parameters
        self.nn_update_path = state_dict_path

        # initialize an optimizer object and a dict to hold dynamic parameters
        self.nn_optimizer = torch.optim.Adam(self.nn.parameters())
        self._dynamic_params = {"optimizer": {"lr": 0.01, "betas": (0.9, 0.999)}}

    def save(self, save_path=None):
        """
        Save the current state dict with authorization to overwrite.
        """
        if save_path is None:
            save_path = self.nn_update_path
        torch.save(self.nn.state_dict(), save_path)

    def adjust_optimizer_params(self):
        """
        Dynamically change parameters of the neural net optimizer.
        Intended to be polymorphic in child classes and to be called per epoch.
        """
        for _group in self.nn_optimizer.param_groups:
            _group.update(self._dynamic_params["optimizer"])

    def predict(self, text):
        """
        End-to-end single-piece prediction from text to class probabilities.
        """
        self.nn.eval()
        vector = self.vectorizer(text)
        logits = self.nn(torch.Tensor(vector).unsqueeze(0))
        probs = F.softmax(logits, dim=-1)
        return probs

    def manifold_trajectory(self, texts, **kwargs):
        """
        (1) vectorize texts
        (2) forward propagate, keeping intermediates
        (3) fit intermediates to 2D manifolds
        (4) fit manifolds using Procrustes shape analysis
        (5) fit shapes to trajectory splines
        :param texts: input texts to calculate the manifold profile from.
        :type texts: list of str
        """
        from hover.representation.manifold import LayerwiseManifold
        from hover.representation.trajectory import manifold_spline

        # step 1 & 2
        vectors = torch.Tensor([self.vectorizer(_text) for _text in texts])
        self.nn.eval()
        intermediates = self.nn.eval_per_layer(vectors)
        intermediates = [_tensor.detach().numpy() for _tensor in intermediates]

        # step 3 & 4
        LM = LayerwiseManifold(intermediates)
        LM.unfold(method="umap")
        seq_arr, disparities = LM.procrustes()
        seq_arr = np.array(seq_arr)

        # step 5
        traj_arr = manifold_spline(np.array(seq_arr), **kwargs)

        return traj_arr, seq_arr, disparities

    def evaluate(self, dev_loader, verbose=1):
        """
        Evaluate the neural network against a dev set.
        """
        self.nn.eval()
        true = []
        pred = []
        for loaded_input, loaded_output, _idx in dev_loader:
            _input_tensor = loaded_input.float()
            _output_tensor = loaded_output.float()

            _logits = self.nn(_input_tensor)
            _true_batch = _output_tensor.argmax(dim=1).detach().numpy()
            _pred_batch = F.softmax(_logits, dim=1).argmax(dim=1).detach().numpy()
            true.append(_true_batch)
            pred.append(_pred_batch)
        true = np.concatenate(true)
        pred = np.concatenate(pred)
        accuracy = classification_accuracy(true, pred)
        conf_mat = confusion_matrix(true, pred)

        if verbose > 0:
            log_info = dict(self._dynamic_params)
            log_info["performance"] = "Acc {0:.3f}".format(accuracy)
            self.logger.info(
                "{0: <80}".format(
                    "Eval: Epoch {epoch} {performance}".format(**log_info)
                )
            )

        return accuracy, conf_mat

    def train(self, train_loader, dev_loader=None, epochs=1, verbose=1):
        """
        Train the neural network.
        This method is a vanilla template and is intended to be overridden in child classes.
        Also intended to be coupled with self.train_batch().
        """
        train_info = []
        for epoch_idx in range(epochs):
            self._dynamic_params["epoch"] = epoch_idx + 1
            self.train_epoch(train_loader, verbose=verbose)
            if dev_loader is not None:
                acc, conf_mat = self.evaluate(dev_loader, verbose=verbose)
                train_info.append({"accuracy": acc, "confusion_matrix": conf_mat})
        return train_info

    def train_epoch(self, train_loader, *args, **kwargs):
        """
        Train the neural network for one epoch.
        Supports flexible args and kwargs for child classes that may implement self.train() and self.train_batch() differently.
        """
        self.adjust_optimizer_params()
        for batch_idx, (loaded_input, loaded_output, index) in enumerate(train_loader):
            self._dynamic_params["batch"] = batch_idx + 1
            self.train_batch(loaded_input, loaded_output, *args, **kwargs)

    def train_batch(self, loaded_input, loaded_output, verbose=1):
        """
        Train the neural network for one batch.
        """
        self.nn.train()
        input_tensor = loaded_input.float()
        output_tensor = loaded_output.float()

        # compute logits
        logits = self.nn(input_tensor)
        loss = cross_entropy_with_probs(logits, output_tensor)

        self.nn_optimizer.zero_grad()
        loss.backward()
        self.nn_optimizer.step()

        if verbose > 0:
            log_info = dict(self._dynamic_params)
            log_info["performance"] = "Loss {0:.3f}".format(loss)
            print(
                "{0: <80}".format(
                    "Train: Epoch {epoch} Batch {batch} {performance}".format(
                        **log_info
                    )
                ),
                end="\r",
            )


class ProdigyTextVectorNet(TextVectorNet):
    """
    Prodigy flavor of the transfer learning model.
    Implements a __call__() method and a update() method for Prodigy.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_accepted = []
        self.cache_rejected = []
        self.base_batch_size = kwargs.get('batch_size', 4)
        self.base_update_threshold = kwargs.get('update_threshold', 16)
        assert self.base_update_threshold // self.base_batch_size >= 1, "Need at least one batch to prepare updates"
        assert self.base_update_threshold % self.base_batch_size == 0, "Whole batches are required to prevent bugs that may occur in custom architectures"

    def __call__(self, stream):
        """
        Generate examples for annotation. Accepts pre-computed overrides by a "proposed" dict.
        :param stream: generator of data entries managed by Prodigy in dictionary format.
        :type stream: iterable
        """
        for _eg in stream:
            _text = _eg.get("text", "")
            # if there is a precomputed override, pop it
            if f"{PRODIGY_KEY_TRANSFORM_PREFIX}proposed" in _eg:
                _proposed_dict = _eg.pop("proposed")
                _label = proposed_dict["label"]
                # attempt to decode the label if it is not already decoded
                _label = self.label_decoder.get(_label, _label)
                _score = proposed_dict["score"]
            else:
                # forward propagation to get class probabilities
                _probs = self.predict(_text).detach().numpy().flatten()

                # finalize label and score
                # the label is sampled rather than argmax so that unbalanced wrong predictions get less troublesome
                _encoded_label = np.random.choice(self.num_classes, p=_probs)
                _label = self.label_decoder[_encoded_label]
                # the score is an unit-scale entropy measure of the class probabilities, i.e. consistent regardless of the number of classes
                _score = unit_scale_entropy(_probs)
            _eg["label"] = _label
            yield (_score, _eg)

    def update(self, answers):
        """
        Update the model weights with the new answers. This method receives
        the examples with an added "answer" key that either maps to "accept",
        "reject" or "ignore".
        :param answers: iterable of Prodigy dicts.
        """
        # update with accepted answers
        self._update_accepted(answers)
        
        # update with rejected answers
        self._update_rejected(answers)
            
    def _update_subroutine(self, send_to_update, batch_size):
        """
        Low-level subroutine for training the active learning model given a list of dicts containing annotations.
        """
        input_vectors = [self.vectorizer(_d["text"]) for _d in send_to_update]
        output_labels = [self.label_encoder[_d["label"]] for _d in send_to_update]
        onehot_labels = one_hot(output_labels, num_classes=self.num_classes)
        output_vectors = label_smoothing(onehot_labels, num_classes=self.num_classes)
        train_loader = vector_dataloader(input_vectors, output_vectors, batch_size=batch_size)
        self.logger.info(
            f"Updating model on {len(send_to_update)} examples with batch size {batch_size}"
        )
        self.train(train_loader, verbose=1)
        self.save()
        
    def _update_accepted(self, answers):
        """
        Train the active learning model with accepted annotations.
        """
        accepted = [_d for _d in answers if _d["answer"] == "accept"]
        self.cache_accepted.extend(accepted)
        
        # if enough samples are present, update parameters
        update_threshold = self.base_update_threshold * 1
        batch_size = self.base_batch_size * 1
        
        num_ready_updates = len(self.cache_accepted) // update_threshold
        if num_ready_updates >= 1:
            update_split = update_threshold * num_ready_updates
            send_to_update = self.cache_accepted[:update_split]
            self.cache_accepted = self.cache_accepted[update_split:]
            self._update_subroutine(send_to_update, batch_size)
    
    def _update_rejected(self, answers):
        """
        Train the active learning model with rejected annotations.
        """
        rejected = [_d for _d in answers if _d["answer"] == "reject"]
        rej_converted = self._convert_rejected_for_training(rejected)
        self.cache_rejected.extend(rej_converted)
        
        # if enough samples are present, update parameters
        update_threshold = self.base_update_threshold * (self.num_classes - 1)
        batch_size = self.base_batch_size * (self.num_classes - 1)
        
        num_ready_updates = len(self.cache_rejected) // update_threshold
        if num_ready_updates >= 1:
            update_split = update_threshold * num_ready_updates
            send_to_update = self.cache_rejected[:update_split]
            self.cache_rejected = self.cache_rejected[update_split:]
            self._update_subroutine(send_to_update, batch_size)
        
    def _convert_rejected_for_training(self, rejected):
        '''
        Subroutine for _update_rejected() to utilize rejected annotations for training.
        '''
        converted = []
        for _rej_dict in rejected:
            _label = _rej_dict["label"]
            for _class in self.label_encoder.keys():
                # skip the rejected class
                if _class == _label:
                    continue
                # update to un-rejected class and append
                _acc_dict = deepcopy(_rej_dict)
                _acc_dict["label"] = _class
                converted.append(_acc_dict)
        return converted
