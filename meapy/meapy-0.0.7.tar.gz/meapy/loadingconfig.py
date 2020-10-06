"""
LoadingConfig is the request config used to fetch signals from MaDaM.

It contains the Template, SignalNames, ...
"""


class LoadingConfig(object):
    def __init__(self):
        self.templateUid = None
        self.signals = []

    def withTemplate(self, uid: str):
        self.templateUid = uid
        return self

    def withSignals(self, signals: list):
        self.signals = signals
        return self

    def getTemplate(self) -> str:
        return self.templateUid

    def getSignals(self) -> list:
        return self.signals
