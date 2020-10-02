from gmrs.evaluation.outcome import Outcome


class Evaluation():
    config: dict = None
    outcomes = []

    def __init__(self, config: dict, outcomes: [Outcome]):
        self.config = config
        self.outcomes = outcomes

