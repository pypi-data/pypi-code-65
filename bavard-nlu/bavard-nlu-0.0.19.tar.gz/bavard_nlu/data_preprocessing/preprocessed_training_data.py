from typing import List
from collections import defaultdict

import tensorflow as tf
from sklearn.preprocessing import LabelEncoder

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
        Converts the examples into a tensor dataset.
        """
        # Unpack each example's dictionary of tensors into a single dictionary
        # containing lists of tensors.
        data = defaultdict(list)
        for example in self.examples:
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
