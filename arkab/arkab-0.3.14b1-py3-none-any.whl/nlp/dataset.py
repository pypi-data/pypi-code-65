from torch.utils.data import Dataset as TDataset
import torch as th
from typing import List, Tuple
from arkab.nlp.knowledge import PATTERNS

TRIPLET = Tuple[int, int, int]

TRIPLETS = List[TRIPLET]


class TripletDataset(TDataset):
    """
    Provided: datasource of TRIPLETS
    """

    def __init__(self, data_source: TRIPLETS,
                 p: PATTERNS = 'hrt', device: th.device = th.device('cpu')):
        self.data_src = data_source
        self.pattern = p
        self.device = device

    def __len__(self):
        return len(self.data_src)

    def __getitem__(self, index):
        item = self.data_src[index]
        if self.pattern == 'hrt':
            head_idx, rel_idx, tail_idx = item
        else:
            head_idx, tail_idx, rel_idx = item

        head_idx = th.tensor(head_idx, device=self.device)
        tail_idx = th.tensor(tail_idx, device=self.device)
        rel_idx = th.tensor(rel_idx, device=self.device)
        return head_idx, rel_idx, tail_idx
