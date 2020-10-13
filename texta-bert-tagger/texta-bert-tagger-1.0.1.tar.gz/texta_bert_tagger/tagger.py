import torch
import os
import json
import pandas as pd
import numpy as np
import time
import datetime
import random
import GPUtil
import dill

from typing import List, Dict, Tuple

from .tagging_report import TaggingReport
from .config import Config

from .validators import ModelExistingValidator, ModelLoadedValidator
from .validators import InputValidator, ArgumentValidator

from transformers import BertTokenizer, BertForSequenceClassification, BertConfig
from transformers import AdamW, get_linear_schedule_with_warmup

from torch.utils.data import DataLoader, TensorDataset
from torch.utils.data import RandomSampler, SequentialSampler
from torch.utils.data import random_split

class BertTagger:
    def __init__(self, display_progress_msgs = True, gpu_max_memory = 0.5, test_mode = False):
        self.config = Config()
        self.test_mode = test_mode

        self.gpu_max_memory = gpu_max_memory
        self.stdout = display_progress_msgs

        self.model = None

        self.tokenizer = None
        self.device = self._get_device()

        self.models_dir = os.path.join(".","saved_models")

        self.optimizer = None
        self.scheduler = None

    def _make_dir(self, _dir):
        if not os.path.exists(_dir):
            os.makedirs(_dir)

    def _print(self, text):
        if self.stdout:
            print(text)

    def _load_json(self, fp):
        with open(fp, "r") as f:
            data = json.load(f)
        return data

    def _dump_json(self, data, fp):
        with open(fp, "w") as f:
            json.dump(data, f)

    def set_models_dir(self, model_dir):
        self.models_dir = model_dir

    def _get_device(self):
        """ Get device to run the process on (GPU, if available, else CPU).
        """
        device = None
        # If there's a GPU available...
        if torch.cuda.is_available():

            # Check if available GPU(s) have required amount of available memory.
            devices = GPUtil.getAvailable(order ="memory", limit=3, maxMemory = self.gpu_max_memory)
            if devices:
                device_id = devices[0]
                torch.cuda.empty_cache()
                device = torch.device("cuda")
                torch.cuda.set_device(device_id)
                self._print(f"We will use the GPU: {torch.cuda.get_device_name(device_id)}")
                self._print(f"Device index: {torch.cuda.current_device()}")

            else:
                device = torch.device("cpu")
                self._print(f"No GPUs available with memory usage <= {self.gpu_max_memory}. Using CPU.")
        else:
            self._print("No GPU available, using the CPU instead.")
            device = torch.device("cpu")
        return device

    def load_pretrained(self, state_dict=None):
        """ Load pretrained BERT model.

        Parameters:
            state_dict - Fine-tuned model's loaded state_dict.
        """
        model = BertForSequenceClassification.from_pretrained(
                   self.config.bert_model,
                   state_dict = state_dict,
                   num_labels = self.config.n_classes,
                   output_attentions = self.config.output_attention_weights,
                   output_hidden_states = self.config.output_hidden_states,
                 )

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            model.cuda()

        return model

    def add_optimizer(self, optimizer):
        self.optimizer = optimizer

    def add_scheduler(self, scheduler):
        self.scheduler = scheduler

    def evaluate_model(self, iterator: DataLoader) -> TaggingReport:
        """ Evaluates the model using evaluation set & Tagging Report.

        Parameters:
            iterator - Instance of torch.utils.data.DataLoader

        Returns:
            report - Instance of TaggingReport containing the results.
        """
        # Measure evaluation time
        t0 = time.time()

        all_preds = []
        all_y = []

        total_eval_loss = 0

        # Put model into evaluation mode
        self.model.eval()

        # Evaluate data for one epoch
        for i, batch in enumerate(iterator):

            # As we unpack the batch, we'll also copy each tensor to the GPU
            b_input_ids  = batch[0].to(self.device)
            b_input_mask = batch[1].to(self.device)
            b_labels     = batch[2].to(self.device)
            b_segment_ids = None

            # Tell pytorch not to bother with constructing the compute graph during
            # the forward pass, since this is only needed for backprop (training).
            with torch.no_grad():
                (loss, logits) = self.model(b_input_ids,
                                       token_type_ids=b_segment_ids,
                                       attention_mask=b_input_mask,
                                       labels=b_labels)

            # Accumulate the validation loss.
            total_eval_loss+=loss.item()

            # Move logits and labels to CPU
            logits = logits.detach().cpu().numpy() # preds
            label_ids = b_labels.to("cpu").numpy()

            preds_flat = np.argmax(logits, axis=1).flatten()
            labels_flat = label_ids

            all_preds.extend(preds_flat)
            all_y.extend(labels_flat)

        # Calculate the average loss over all of the batches.
        avg_loss = total_eval_loss / len(iterator)

        # Measure how long the validation run took.
        time_elapsed = time.time() - t0

        report = TaggingReport(all_y, all_preds)
        report.validation_time = time_elapsed
        report.validation_loss = avg_loss

        return report

    def _run_epoch(self, train_iterator: DataLoader,
                         val_iterator: DataLoader,
                         epoch: int) -> TaggingReport:
        """ Run one training epoch epoch.

        Parameters:
            train_iterator - Iterator containing training data.
            val_iterator   - Iterator containing validation data.
            epoch - epoch number.

        Returns:
            report - Instance of TaggingReport containg results for one epoch.
        """

        # Measure how long the training epoch takes.
        t0 = time.time()

        # Reset the total loss for this epoch.
        total_train_loss = 0

        # Put the model into training mode.
        self.model.train()

        # For each batch of training data...
        for i, batch in enumerate(train_iterator):
            # Unpack this training batch from our dataloader.
            #
            # As we unpack the batch, we'll also copy each tensor to the GPU
            b_input_ids   = batch[0].to(self.device)
            b_input_mask  = batch[1].to(self.device)
            b_labels      = batch[2].to(self.device)
            b_segment_ids = None

            # Always clear any previously calculated gradients before performing a
            # backward pass. PyTorch doesn't do this automatically because
            # accumulating the gradients is "convenient while training RNNs".
            self.model.zero_grad()

            # Perform a forward pass (evaluate the model on this training batch).
            loss, logits = self.model(b_input_ids,
                                      token_type_ids = b_segment_ids,
                                      attention_mask = b_input_mask,
                                      labels = b_labels)

            # Accumulate the training loss.
            total_train_loss += loss.item()

            # Perform a backward pass to calculate the gradients.
            loss.backward()

            # Clip the norm of the gradients to 1.0.
            # This is to help prevent the "exploding gradients" problem.
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)

            # Update parameters and take a step using the computed gradient.
            # The optimizer dictates the "update rule"--how the parameters are
            # modified based on their gradients, the learning rate, etc.
            self.optimizer.step()

            # Update the learning rate.
            self.scheduler.step()

        # Calculate the average loss over all of the batches.
        avg_train_loss = total_train_loss / len(train_iterator)

        # Measure how long this epoch took.
        training_time = time.time() - t0

        report = self.evaluate_model(val_iterator)

        # Add training time, training_loss and epoch number to report
        report.training_time = training_time
        report.training_loss = avg_train_loss
        report.epoch = epoch

        return report

    def load_tokenizer(self):
        """ Load pretrained BERT tokenizer.
        """
        self.tokenizer = BertTokenizer.from_pretrained(self.config.bert_model)
        return self.tokenizer

    def tokenize(self, sentences: List[str], labels: list=[]):
        """ Tokenize all the sentences and map the tokens to their corresponding IDs.

        Parameters:
            sentences - List of (short) texts.
            labels - Labels corresponding to each text.

        Returns:
            input_ids - IDs corresponding to each token.
            attention_mask - Attention masks.
            labels - Labels as torch.tensors instance.

        """
        self.load_tokenizer()

        input_ids = []
        attention_masks = []

        # For every sentence...
        for sentence in sentences:
            # `encode_plus` will:
            #   (1) Tokenize the sentence.
            #   (2) Prepend the `[CLS]` token to the start.
            #   (3) Append the `[SEP]` token to the end.
            #   (4) Map tokens to their IDs.
            #   (5) Pad or truncate the sentence to `max_length`
            #   (6) Create attention masks for [PAD] tokens.
            encoded_dict = self.tokenizer.encode_plus(
                                sentence,
                                add_special_tokens = self.config.add_special_tokens,
                                max_length = self.config.max_length,
                                padding = self.config.padding,
                                truncation = self.config.truncation,
                                return_attention_mask = self.config.return_attention_mask,
                                return_tensors = self.config.return_tensors
                           )

            # Add the encoded sentence to the list.
            input_ids.append(encoded_dict["input_ids"])

            # And its attention mask (simply differentiates padding from non-padding).
            attention_masks.append(encoded_dict["attention_mask"])

        # Convert the lists into tensors.
        input_ids = torch.cat(input_ids, dim=0)
        attention_masks = torch.cat(attention_masks, dim=0)
        #if labels:
        labels = torch.tensor(labels)

        return (input_ids, attention_masks, labels)

    def _get_dataset(self, input_ids, attention_masks, labels=[]) -> TensorDataset:
        """ Combine the training inputs into a TensorDataset.

        Parameters:
            input_ids - tokenizer output IDs as torch tensors.
            attention_masks - tokenizer output attention_masks as torch tensors.
            labels - tokenizer output labels as torch tensors.

        """
        if isinstance(labels, list) and not labels:
            dataset = TensorDataset(input_ids, attention_masks)
        else:
            dataset = TensorDataset(input_ids, attention_masks, labels)
        return dataset

    def _split_dataset(self, dataset: TensorDataset) -> Tuple[TensorDataset, TensorDataset]:
        """ Split dataset into training and validation set.

        Parameters:
            dataset - TensorDataset instance to split.

        Returns:
            train_dataset - TensorDataset instance containing training examples.
            val_dataset - TensorDataset instance containing validation examples.
        """
        # Calculate the number of samples to include in each set.
        train_size = int(self.config.split_ratio * len(dataset))
        val_size = len(dataset) - train_size

        # Divide the dataset by randomly selecting samples.
        train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

        return (train_dataset, val_dataset)

    def _get_iterator(self, dataset: TensorDataset,
                            dataset_type: str = "train") -> DataLoader :
        """ Get DataLoader based on dataset type (random for training,
            sequential for validation.

        Parameters:
            dataset - TensorDataset instance to iterate.
            dataset_type - Indicatior if dataset is used for training or validation.

        Returns:
            iterator - Instance of type DataLoader for iterating over datasets.
        """
        if dataset_type == "train":
            sampler = RandomSampler(dataset)
        else:
            sampler = SequentialSampler(dataset)
        iterator = DataLoader(dataset, sampler=sampler, batch_size=self.config.batch_size)
        return iterator

    def get_optimizer(self) -> AdamW:
        """ Get AdamW optimizer for training the model.

        Returns:
            optimizer - AdamW optimizer.
        """
        ModelLoadedValidator().validate(self.model)
        # Note: AdamW is a class from the huggingface library (as opposed to pytorch)
        optimizer = AdamW( self.model.parameters(),
                           lr  = self.config.lr,
                           eps = self.config.eps
                         )
        return optimizer

    def get_scheduler(self, n_training_batches: int, optimizer: AdamW):
        """ Get learning rate scheduler.

        Parameters:
            n_training_batches - Number of training batches.
            optimizer - AdamW optimizer.

        Returns:
            scheduler - Learning rate scheduler.
        """
        # Total number of training steps is [number of batches] x [number of epochs].
        # (Note that this is not the same as the number of training samples).
        total_steps = n_training_batches * self.config.n_epochs

        # Create the learning rate scheduler.
        scheduler = get_linear_schedule_with_warmup(
                        optimizer,
                        num_warmup_steps = 0, # Default value in run_glue.py
                        num_training_steps = total_steps
                    )
        return scheduler

    def _get_examples_and_labels(self, data_sample: Dict[str, List[str]]) -> Tuple[List[str], List[int]]:
        """ Extract examples and labels from data_samples.

        Parameters:
            data_sample - TODO

        Returns:
            examples - Training (and validation) examples.
            labels - Labels corresponding to each example.
        """
        examples = []
        labels = []

        # Retrieve examples for each class
        for label, class_examples in data_sample.items():
            for example in class_examples:
                examples.append(example)
                labels.append(self.config.label_index[label])

        return (examples, labels)

    def _create_label_indices(self, data_sample: Dict[str, List[str]]):
        """ Create label indices.
        """
        self.config.label_index = {a: i for i, a in enumerate(data_sample.keys())}
        self.config.label_reverse_index = {b: a for a, b in self.config.label_index.items()}

    def _prepare_data(self, data_sample: Dict[str, List[str]]) -> Tuple[DataLoader, DataLoader]:
        """ Prepare training data.
        """
        self._print("Preparing data...")
        self.config.n_classes = len(data_sample)

        self._create_label_indices(data_sample)

        sentences, labels = self._get_examples_and_labels(data_sample)

        self._print(f"Using trainset size {len(sentences)}...")
        self._print(f"Tokenizing data...")

        input_ids, attention_masks, labels = self.tokenize(sentences, labels)
        dataset = self._get_dataset(input_ids, attention_masks, labels)
        train_dataset, val_dataset = self._split_dataset(dataset)

        train_iterator = self._get_iterator(train_dataset, "train")
        val_iterator = self._get_iterator(val_dataset, "validation")

        return (train_iterator, val_iterator)

    def update_config(self, **kwargs):
        """ Update configuration.
        """
        ArgumentValidator().validate_arguments(**kwargs)
        self.config.update_bulk(kwargs)
        return True

    def _set_seeds(self):
        random.seed(self.config.seed_val)
        np.random.seed(self.config.seed_val)
        torch.manual_seed(self.config.seed_val)
        torch.cuda.manual_seed_all(self.config.seed_val)


    def train(self, data_sample: Dict[str, List[str]], **kwargs) -> TaggingReport:
        """ Fine-tune BERT model.

        Parameters:
            data_sample - Training (and valiation) data as dict where
                          keys = labels, values = example texts.

        """
        InputValidator().validate(data_sample, **kwargs)

        self.update_config(**kwargs)
        train_iterator, val_iterator = self._prepare_data(data_sample)

        # Set the seed value all over the place to make this reproducible.
        self._set_seeds()

        n_training_batches = len(train_iterator)

        # Measure the total training time for the whole run.
        total_t0 = time.time()
        self.epoch_reports = []

        self.model = self.load_pretrained()

        optimizer = self.get_optimizer()
        scheduler = self.get_scheduler(n_training_batches, optimizer)

        self.add_optimizer(optimizer)
        self.add_scheduler(scheduler)

        self._print("Start training...")

        # For each epoch...
        for epoch_i in range(self.config.n_epochs):
            self._print(f"Running epoch {epoch_i+1}/{self.config.n_epochs}...")

            report = self._run_epoch(train_iterator, val_iterator, epoch_i)
            self.epoch_reports.append(report)

        self._print("Finished training!")

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return report

    def tag_text(self, text: str) -> str:
        """ Tag text with previously loaded or trained model.

        Parameters:
            text - Text to tag.

        Returns:
            predicted_label - Predicted label for input text.
        """
        ModelLoadedValidator().validate(self.model)

        input_ids, attention_masks, labels = self.tokenize([text])
        prediction_dataset = self._get_dataset(input_ids, attention_masks)
        prediction_iterator= self._get_iterator(prediction_dataset)

        # Put model in evaluation mode
        self.model.eval()

        # Tracking variables
        predictions = []

        # Predict
        for batch in prediction_iterator:
            # Add batch to GPU
            batch = tuple(t.to(self.device) for t in batch)

            # Unpack the inputs from our dataloader
            b_input_ids, b_input_mask = batch

            # Telling the model not to compute or store gradients, saving memory and
            # speeding up prediction
            with torch.no_grad():
                # Forward pass, calculate logit predictions
                outputs = self.model(b_input_ids, token_type_ids=None,
                                     attention_mask=b_input_mask)

            logits = outputs[0]

            # Move logits and labels to CPU
            logits = logits.detach().cpu().numpy()

            # Store predictions and true labels
            predictions.append(logits)

        flat_predictions = np.concatenate(predictions, axis=0)

        # For each sample, pick the label (0 or 1) with the higher score.
        flat_predictions = np.argmax(flat_predictions, axis=1).flatten()

        prediction = flat_predictions[0]
        predicted_label = self.config.label_reverse_index[prediction]

        return predicted_label

    def _get_new_model_id(self) -> str:
        """ Get ID for new model.
        """

        self._make_dir(self.models_dir)
        saved_models = os.listdir(self.models_dir)

        n_saved_models = len(saved_models)

        # Presume models are numbered sequentelly from 1
        new_id = n_saved_models + 1

        # ... But check to make sure. Increment id while it
        # is present in save_models.
        while str(new_id) in saved_models:
            new_id+=1

        self._print(f"{new_id} not in saved models!")

        return str(new_id)

    def save(self, path: str = ""):
        """ Save fine-tuned model.

        Parameters:
            path - Path of the file where the model is saved.
        """
        if not path:
            model_id = self._get_new_model_id()
            path = os.path.join(self.models_dir, model_id)
        directory = directory = os.path.dirname(path)
        self._make_dir(directory)

        to_save = {"tagger_conf": self.config.to_dict(),
                   "model": self.model}

        with open(path, "wb") as f:
            dill.dump(to_save, f)

        self._print(f"Model saved to: {path}")

    def _set_loaded_values(self, loaded):
        self.model = loaded["model"]
        self.config.update_bulk(loaded["tagger_conf"])
        
        # Assign model to current device
        if not self.test_mode:
            self.model.to(self.device)

    def load(self, path: str):
        """ Load fine-tuned model.

        Parameters:
            path - Path to model file.
        """
        ModelExistingValidator().validate_saved_model(path)

        with open(path, "rb") as f:
            loaded = dill.load(f)

        self._set_loaded_values(loaded)
        return True
