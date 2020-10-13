import unittest
import os
from zzpy import load_matcher, load_matchers, match_area


class TestCase(unittest.TestCase):
    def test_load_matcher(self):
        def _match(config, area_a, area_b):
            return load_matcher(config)(area_a, area_b)
        self.assertTrue(_match(config={"pattern_a": "A|B|C", "pattern_b": "A|B|C"}, area_a=(
            "A", "B", "C"), area_b=("A", "B", "C")))
        self.assertTrue(_match(config={"pattern_a": ".*|.*|.*", "pattern_b": "{province}|{city}|{district}"}, area_a=(
            "A", "B", "C"), area_b=("A", "B", "C")))
        self.assertFalse(_match(config={"pattern_a": ".*|.*|.*", "pattern_b": "{province}|{city}|{district}"}, area_a=(
            "A", "B", "C"), area_b=("A", "B", "D")))
        self.assertTrue(_match(config={"pattern_a": ".*|.*|.*", "pattern_b": "{province}|{city}|.*"}, area_a=(
            "A", "B", "C"), area_b=("A", "B", "D")))

    def test_match_area(self):
        mathcers = load_matchers(os.path.join(
            "test", "static", "match_config.jsonl"))

        def _match(area_a, area_b):
            return match_area(mathcers, area_a, area_b)

        self.assertTrue(_match(("北京市", "北京市", "东城区"), ("北京市", "北京市", "东城区")))
        self.assertTrue(_match(("北京市", "北京市", "东城区"), ("北京市", "北京市", "西城区")))
        self.assertFalse(_match(("北京市", "北京市", "东城区"), ("北京市", "XXX", "西城区")))
        self.assertTrue(_match(("重庆市", "XXX", "YYY"), ("重庆市", "AAA", "BBB")))
