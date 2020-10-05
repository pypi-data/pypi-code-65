"""Geo module."""


class Wt:

    def __init__(self, to, fro):
        self.to = to
        self.fro = fro

    # @classmethod
    def convert_to(self):
        return self.to

    # @classmethod
    def convert_from(self):
        return self.fro


class Gh:

    def __init__(self, gh):
        self.gh = gh
        self.la = None
        self.lo = None
