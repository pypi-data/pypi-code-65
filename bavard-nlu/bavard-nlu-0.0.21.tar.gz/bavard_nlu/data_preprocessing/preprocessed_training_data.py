from typing import List
from collections import defaultdict

import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

from bavard_nlu.data_preprocessing.training_example import Example


class PreprocessedTrainingData:
    def __init__(self, intents: List[str], tag_types: List[str], examples: List[Example]):
        self.intents = intents
        self.tag_types = tag_types
        self.examples = examples

        tag_set = {'[CLS]', '[SEP]', 'O'}
        for tag_type in self.tag_types:
            tag_set.add(f'B-{tag_type}')
            tag_set.add(f'I-{tag_type}')

        self.tag_encoder = LabelEncoder()
        self.tag_encoder.fit(list(tag_set))
        self.intents_encoder = LabelEncoder()
        self.intents_encoder.fit(self.intents)
    
    def to_dataset(self, max_seq_len: int) -> tf.data.Dataset:
        """
        Converts this instance's examples into a tensor dataset.
        """
        return self._to_dataset(max_seq_len, self.examples)
    
    def to_dataset_split(
        self,
        max_seq_len: int,
        split_ratio: float,
        shuffle: bool = True,
        seed: int = 0
    ) -> tuple:
        """
        Converts this instance's examples into two tensor datasets, stratified
        by the intent label.
        """
        intent_labels = [ex.intent for ex in self.examples]
        examples_a, examples_b = train_test_split(
            self.examples, test_size=split_ratio, random_state=seed, shuffle=shuffle, stratify=intent_labels
        )

        return self._to_dataset(max_seq_len, examples_a), self._to_dataset(max_seq_len, examples_b)

    def _to_dataset(self, max_seq_len: int, examples: List[Example]) -> tf.data.Dataset:
        # Unpack each example's dictionary of tensors into a single dictionary
        # containing lists of tensors.
        data = defaultdict(list)
        for example in examples:
            tensor_dict = example.to_tensors(max_seq_len, self.tag_encoder, self.intents_encoder)
            for key in tensor_dict:
                data[key].append(tensor_dict[key])
        
        # Now convert those lists to tensors
        for key in data:
            data[key] = tf.stack(data[key])

        # Next, split them into X and Y.
        X = {k: data[k] for k in ["input_ids", "input_mask", "word_start_mask"]}
        Y = {k: data[k] for k in ["intent", "tags"]}

        return tf.data.Dataset.from_tensor_slices((X, Y))
