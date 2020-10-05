# Base Filelist dataset and conversion class
# Override your own decoder() function to decode from raw data,
# and your own encoder() function to convert your data to LMDB.

# Based on Pytorch-lightning for abstract research code from engineering code.
# Reference and adapted from:
# https://pytorch-lightning.readthedocs.io/en/latest/lightning-module.html
# https://github.com/Lyken17/Efficient-PyTorch/blob/master/tools/folder2lmdb.py
# Author: Xiao Li

from typing import Callable, Optional

import torch.utils.data as data
import pickle


class DatasetFilelist(data.Dataset):
    r"""
    Base class of flielist dataset.
    Inherit this class and implement dataset-specifc logic (e.g. data decode / augmentation)
    """

    def __init__(self,
                 path_of_filelist: str, decoder: Optional[Callable] = None,
                 transform: Optional[Callable] = None, target_transform: Optional[Callable] = None):
        self.path_of_filelist = path_of_filelist
        with open(path_of_filelist, 'rb') as f:
            self.list_of_file_dict = pickle.load(f)

        self.length = len(self.list_of_file_dict)

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

        file_dict = self.list_of_file_dict[index]
        decoded_data = self.decoder(file_dict)

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
