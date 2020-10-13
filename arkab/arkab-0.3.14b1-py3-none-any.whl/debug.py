from torch.utils.data import DataLoader, Dataset
from typing import Literal
import torch

RETURN_TYPES = Literal['dict', 'tuple']


def debug_dataset(dataset: Dataset):
    r"""

    :param dataset: dataset for debug
    """
    dataloader = DataLoader(dataset=dataset, batch_size=1)
    for i, item in enumerate(dataloader):
        if i == 1:
            return
        assert item is not None, f"dataset __get__(index) return None"
        if isinstance(item, tuple):
            print(f"Return {len(item)} data.")
            for e, j in enumerate(item):
                if isinstance(j, torch.Tensor):
                    print(f"the {e}-th item is tensor with shape {j.shape}")
                else:
                    print(f"the {e}-th item {j=}")
        elif isinstance(item, dict):
            for k, v in item.items():
                print(f"Key {k} with Value type{type(v)}")
                if isinstance(v, torch.Tensor):
                    print(f"Tensor value shape {v.shape}")

