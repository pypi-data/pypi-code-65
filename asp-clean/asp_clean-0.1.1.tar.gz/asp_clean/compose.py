import random
from typing import Iterable

def shuffle_compose(doc:dict, random_state=42):
    tmp = [f"{k}: {v}" for k, v in doc.items()]
    random.seed(42)
    random.shuffle(tmp)
    return " ".join(tmp)

class Composer(object):
    def __init__(self, connector="is"):
        self.connector: str = connector

    def compose_report(self, doc: dict, ratio: float = 1.0, shuffle=True):
        if shuffle:
            selected_keys = self._sample_keys(doc, ratio)
        else:
            selected_keys = list(doc.keys())
        content = self._arrange_content(doc, selected_keys)
        return content

    def _arrange_content(self, doc: dict, selected_keys: Iterable[str]):
        return " ".join(
            f"{key.title()} {self.connector} {doc[key].lower()}"
            for key in selected_keys
        )

    def _sample_keys(self, doc: dict, ratio: float) -> list:
        keys = set(doc.keys())

        if 0 > ratio or ratio > 1:
            print("0 < Ratio < 1. Use default composing ratio: 0.5")
            ratio = 0.5
        sample_size = round(len(keys) * ratio)
        selected_keys = random.sample(keys, sample_size)

        return selected_keys
