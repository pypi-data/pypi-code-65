# Base LMDB dataset and conversion class
# Override your own decoder() function to decode from raw data,
# and your own encoder() function to convert your data to LMDB.

# Based on Pytorch-lightning for abstract research code from engineering code.
# Reference and adapted from:
# https://pytorch-lightning.readthedocs.io/en/latest/lightning-module.html
# https://github.com/Lyken17/Efficient-PyTorch/blob/master/tools/folder2lmdb.py
# Author: Xiao Li

from typing import Callable, Optional

import os

import torch
import torch.utils.data as data
import lmdb
import pyarrow as pa


class DatasetLMDB(data.Dataset):
    r"""
    Ref and adapted from:
    https://github.com/Lyken17/Efficient-PyTorch/blob/master/tools/folder2lmdb.py
    Base class of LMDB dataset.
    Inherit this class and implement dataset-specifc logic (e.g. data decode / augmentation)
    Note: Please ensure transform() return a dict struct.
    """

    def __init__(self,
                 db_path: str, decoder: Optional[Callable] = None,
                 transform: Optional[Callable] = None, target_transform: Optional[Callable] = None):
        self.db_path = db_path
        self.env = lmdb.open(db_path, subdir=os.path.isdir(db_path),
                             readonly=True, lock=False,
                             readahead=False, meminit=False)

        with self.env.begin(write=False) as txn:
            # self.length = txn.stat()['entries'] - 1
            self.length = pa.deserialize(txn.get(b'__len__')) - 1
            self.keys = pa.deserialize(txn.get(b'__keys__'))

        # Override decoder transform if given (Not recommend).
        # A better way to keep code clean is to inherit this class,
        # Then implement the decoder and transform in the class.
        if(decoder is not None):
            self.decoder = decoder
        if(transform is not None):
            self.transform = transform
        if(target_transform is not None):
            self.target_transform = target_transform

        if(not hasattr(self, 'transform')):
            self.transform = None
        if(not hasattr(self, 'target_transform')):
            self.target_transform = None

    def __getitem__(self, index):
        data_input, data_target = None, None

        env = self.env
        with env.begin(write=False) as txn:
            byteflow = txn.get(self.keys[index])
        unpacked = pa.deserialize(byteflow)

        decoded_data = self.decoder(unpacked)
        data_input, data_target = decoded_data['data_input'], decoded_data['data_target']

        if(self.transform is not None):
            data_input = self.transform(data_input)

        if(data_target is not None and self.target_transform is not None):
            data_target = self.target_transform(data_target)

        # if data_target and data_input both exists, return a dict that merge them
        assert(isinstance(data_input, dict) and (isinstance(data_target, dict) or data_target is None))
        if(data_target is not None):
            return {**data_input, **data_target}
        else:
            return data_input

    def __len__(self):
        return self.length

    def __repr__(self):
        return self.__class__.__name__ + ' (' + self.db_path + ')'

    # Default: return raw_data from lmdb.
    # Please override this function in inherited class.
    def decoder(self, raw_data):
        return dict(data_input=raw_data, data_target=None)
