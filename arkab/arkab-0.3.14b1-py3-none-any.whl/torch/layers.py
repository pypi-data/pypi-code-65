import torch
from torch.nn import functional as F


class Flatten(torch.nn.Module):
    def __init__(self):
        super(Flatten, self).__init__()

    def forward(self, vec_t):
        return vec_t.view(vec_t.size(0), -1)

    __call__ = forward


class ArEmbedding:
    def __init__(self, weights: torch.Tensor):
        assert len(weights.shape) == 2
        self.weights = weights

    def forward(self, idx: torch.Tensor):
        return F.embedding(input=idx, weight=self.weights)

    __call__ = forward
