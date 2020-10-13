import json
from unittest import TestCase

from bavard_nlu.data_preprocessing.data_preprocessor import DataPreprocessor
from bavard_nlu.model import NLUModel


class TestDataPreprocessor(TestCase):
    def setUp(self):
        super().setUp()
        self.tokenizer = NLUModel.get_tokenizer()
        with open("test_data/test-agent.json") as f:
            self.agent_data = json.load(f)
        self.training_data = DataPreprocessor.preprocess(self.agent_data, self.tokenizer)
        self.example = self.training_data.examples[1]

    def test_preprocess_text(self) -> None:
        text_tokens, word_start_mask, word_to_token_map = DataPreprocessor.preprocess_text(
            "What is the cheapest flight?",
            self.tokenizer
        )
        self.assertEqual(
            text_tokens,
            ['what', 'is', 'the', 'che', '##ap', '##est', 'flight', '?']
        )
        self.assertEqual(word_start_mask, [1, 1, 1, 1, 0, 0, 1, 0])
        self.assertEqual(word_to_token_map, [0, 1, 2, 3, 6])

    def test_preprocess(self) -> None:
        # Check that the tags were identified and aligned correctly.
        self.assertEqual(
            self.example.token_tags,
            ['[CLS]', 'O', 'O', 'O', 'B-flight_stop', 'O', 'O', 'O', 'B-fromloc.city_name', 'I-fromloc.city_name', 'I-fromloc.city_name', 'O', 'B-toloc.city_name', 'I-toloc.city_name', 'I-toloc.city_name', 'O', '[SEP]']
        )
        # Check that the tokens are represented correctly.
        self.assertEqual(
            self.example.tokens,
            ['[CLS]', 'are', 'they', 'all', 'non', '##stop', 'flights', 'from', 'kans', '##as', 'city', 'to', 'st', '.', 'pau', '##l', '[SEP]']
        )

    def test_to_tensor(self) -> None:
        max_seq_length = 200
        tensor_dict = self.example.to_tensors(
            max_seq_length,
            self.training_data.tag_encoder,
            self.training_data.intents_encoder
        )

        # Check that the example was turned into tensors of the correct
        # shapes.
        expected_shapes = {
            "input_ids": (max_seq_length,),
            "input_mask": (max_seq_length,),
            "word_start_mask": (max_seq_length,),
            "intent": (1,),
            "tags": (max_seq_length,)
        }
        for key, expected_shape in expected_shapes.items():
            self.assertEqual(tensor_dict[key].numpy().shape, expected_shape)
