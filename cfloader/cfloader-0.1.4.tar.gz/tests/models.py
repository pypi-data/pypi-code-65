from typing import Optional

class DummyModelWithoutParams:
    def __init__(self):
        pass

class DummyModelWithParams:
    def __init__(self, epochs, batch_size):
        self.epochs = epochs
        self.batch_size = batch_size

class DummyDependency:
    def __init__(self, secondary_dependency: Optional["DummyDependency"] = None):
        self.dependency = secondary_dependency

class DummyEmbedding:
    def __init__(self, vocab_size: int, dim: int):
        self.vocab_size = vocab_size
        self.dim = dim

class DummyModelWithDependency:
    def __init__(self, embedding: DummyEmbedding, dependency: DummyDependency, embedding_size: int):
        self.embedding = embedding
        self.dependency = dependency
        self.embedding_size = embedding_size