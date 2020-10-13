import json
from unittest import TestCase

from bavard_nlu.model import NLUModel


class TestPerformance(TestCase):
    def setUp(self):
        super().setUp()
        self.max_seq_len = 200
        with open("test_data/bavard.json") as f:
            self.agent_data = json.load(f)
    
    def test_model_performance(self):
        # A model fully trained on a dataset representative of what
        # we might see in production should give good generalizeable
        # predictive performance.
        model = NLUModel(self.agent_data, self.max_seq_len)
        model.build_and_compile_model()
        
        train_performance, test_performance = model.evaluate(auto=True)
        self.assertGreaterEqual(train_performance["intent_acc"], .9)
        # TODO: Do a little architecture exploration so this
        # benchmark can be higher.
        self.assertGreaterEqual(test_performance["intent_acc"], .6)
