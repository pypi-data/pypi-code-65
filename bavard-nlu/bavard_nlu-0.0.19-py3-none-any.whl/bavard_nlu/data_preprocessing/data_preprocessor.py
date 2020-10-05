from typing import List

from transformers import DistilBertTokenizerFast

from bavard_nlu import utils
from bavard_nlu.data_preprocessing.preprocessed_training_data import PreprocessedTrainingData
from bavard_nlu.data_preprocessing.training_example import Example, Tag


class DataPreprocessor:
    @staticmethod
    def preprocess_text(text: str, tokenizer: DistilBertTokenizerFast):
        text = text.lower()
        text_words = text.split()
        text_tokens = []
        token_to_word_idx = []
        word_to_token_map = []
        word_start_mask = []
        for (wi, word) in enumerate(text_words):
            word_to_token_map.append(len(text_tokens))
            word_tokens = tokenizer.tokenize(word)
            for ti, token in enumerate(word_tokens):
                token_to_word_idx.append(wi)
                text_tokens.append(token)

                if ti == 0:
                    word_start_mask.append(1)
                else:
                    word_start_mask.append(0)

        return text_tokens, word_start_mask, word_to_token_map

    @staticmethod
    def preprocess(agent_data: dict, tokenizer: DistilBertTokenizerFast) -> PreprocessedTrainingData:
        result_examples: List[Example] = []

        nlu_data = agent_data['nluData']

        intents = nlu_data['intents']
        tag_types = nlu_data['tagTypes']
        examples = nlu_data['examples']

        for ex in examples:
            text = ex['text'].lower()
            intent = ex['intent']
            raw_tags = ex['tags']

            text_tokens, word_start_mask, word_to_token_map = DataPreprocessor.preprocess_text(text, tokenizer)

            char_to_word_map = utils.get_char_to_word_map(text)

            result_tags: List[Tag] = []
            for tag in raw_tags:
                start = tag['start']
                end = tag['end']
                tag_type = tag['tagType']

                start_word_idx = char_to_word_map[start]
                end_word_idx = char_to_word_map[end - 1]

                start_tok = word_to_token_map[start_word_idx]
                end_tok = word_to_token_map[end_word_idx]
                result_tags.append(Tag(tag_type=tag_type,
                                       start=start,
                                       end=end,
                                       start_tok=start_tok,
                                       end_tok=end_tok))

            result_examples.append(Example(
                text=text,
                intent=intent,
                tokens=text_tokens,
                tags=result_tags,
                word_start_mask=word_start_mask,
                tokenizer=tokenizer,
            ))
        return PreprocessedTrainingData(intents=intents, tag_types=tag_types, examples=result_examples)
