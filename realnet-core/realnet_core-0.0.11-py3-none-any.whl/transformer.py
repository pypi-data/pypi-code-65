from abc import ABC, abstractmethod


class Transformer(ABC):

    def __init__(self, func):
        self.func = func

    def pre_transform(self, *args, **kwargs):
        pass

    @abstractmethod
    def transform(self, *args, **kwargs):
        pass

    def post_transform(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        self.pre_transform(args, kwargs)
        result = self.transform(args, kwargs)
        self.post_transform(args, kwargs)
        return result


class ScriptTransformer(Transformer):

    def transform(self, *args, **kwargs):
        pass


class TypeTransformer(Transformer):

    def transform(self, *args, **kwargs):
        pass


class DataTransformer(Transformer):

    def transform(self, *args, **kwargs):
        pass