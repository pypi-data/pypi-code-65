import os
import os.path as osp
import time
import torch
import opentool
from torch.optim import Optimizer
from collections import OrderedDict


def load_checkpoint(filename,
                    logger=None):
    if os.path.isfile(filename):
        checkpoint = torch.load(filename)
        if not isinstance(checkpoint, dict):
            raise RuntimeError(
                f'No state_dict found in checkpoint file {filename}')
    else:
        logger.info("no checkpoint found at '{}'".format(filename))
    return checkpoint


def weights_to_cpu(state_dict):
    """Copy a model state_dict to cpu.

    Args:
        state_dict (OrderedDict): Model weights on GPU.

    Returns:
        OrderedDict: Model weights on GPU.
    """
    state_dict_cpu = OrderedDict()
    for key, val in state_dict.items():
        state_dict_cpu[key] = val.cpu()
    return state_dict_cpu


def save_checkpoint(model, filename, device_ids, optimizer=None, meta=None):
    """Save checkpoint to file.

    The checkpoint will have 3 fields: ``meta``, ``state_dict`` and
    ``optimizer``. By default ``meta`` will contain version and time info.

    Args:
        model (Module): Module whose params are to be saved.
        filename (str): Checkpoint filename.
        optimizer (:obj:`Optimizer`, optional): Optimizer to be saved.
        meta (dict, optional): Metadata to be saved in checkpoint.
    """
    if meta is None:
        meta = {}
    elif not isinstance(meta, dict):
        raise TypeError(f'meta must be a dict or None, but got {type(meta)}')
    meta.update(opentool_version=opentool.__version__, time=time.asctime())

    opentool.mkdir_or_exist(osp.dirname(filename))

    if len(device_ids) > 1:
        state_dict = model.module.state_dict()
    else:
        state_dict = model.state_dict()

    checkpoint = {
        'meta': meta,
        'state_dict': weights_to_cpu(state_dict)
    }
    # save optimizer state dict in the checkpoint
    if isinstance(optimizer, Optimizer):
        checkpoint['optimizer'] = optimizer.state_dict()
    elif isinstance(optimizer, dict):
        checkpoint['optimizer'] = {}
        for name, optim in optimizer.items():
            checkpoint['optimizer'][name] = optim.state_dict()
    # immediately flush buffer
    with open(filename, 'wb') as f:
        torch.save(checkpoint, f)
        f.flush()
