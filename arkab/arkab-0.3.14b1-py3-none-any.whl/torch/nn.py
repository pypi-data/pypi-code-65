import torch


class Flatten(torch.nn.Module):
    def __init__(self):
        super(Flatten, self).__init__()

    def forward(self, vec_t):
        return vec_t.view(vec_t.size(0), -1)


def load_pt_pretrain(file: str, freeze: bool=True) -> torch.nn.Embedding:
    pretrain: torch.Tensor = torch.load(file)
    _num, _dim = pretrain.shape
    embedding = torch.nn.Embedding(num_embeddings=_num, embedding_dim=_dim)
    embedding.from_pretrained(pretrain, freeze=freeze)
    return embedding
