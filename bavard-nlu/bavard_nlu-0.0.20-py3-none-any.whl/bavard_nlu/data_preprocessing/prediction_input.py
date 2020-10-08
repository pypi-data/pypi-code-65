import tensorflow as tf
from transformers import DistilBertTokenizerFast

from bavard_nlu.data_preprocessing.data_preprocessor import DataPreprocessor


class PredictionInput:
    def __init__(self,
                 text: str,
                 max_seq_len: int,
                 tokenizer: DistilBertTokenizerFast):
        self.text = text.lower()
        tokens, word_start_mask, word_to_token_map = DataPreprocessor.preprocess_text(self.text, tokenizer)

        self.tokens = ['[CLS]', *tokens, '[SEP]']
        self.input_ids = tokenizer.convert_tokens_to_ids(self.tokens)
        self.input_mask = [1] * len(self.tokens)
        self.word_start_mask = [0, *word_start_mask, 0]

        while len(self.input_ids) < max_seq_len:
            self.input_ids.append(0)
            self.input_mask.append(0)
            self.word_start_mask.append(0)

    def to_model_input(self):
        return {
            'input_ids': tf.convert_to_tensor([self.input_ids]),
            'input_mask': tf.convert_to_tensor([self.input_mask]),
            'word_start_mask': tf.convert_to_tensor([self.word_start_mask]),
        }
