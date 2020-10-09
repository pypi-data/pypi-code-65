import os.path as osp
from abc import ABCMeta, abstractmethod
from tensorboardX import SummaryWriter
import torch
import logging
import opentool
from .utils import get_time_str
from .checkpoint import load_checkpoint


class BaseRunner(metaclass=ABCMeta):
    """ The base class of Runner, a training helper for Pytorch.

    All subclasses should implement the following APIs:
    - ``train()``
    - ``val()``
    - ``save_checkpoint()``
    Args:
        work_dir (str, optional): The working directory to save checkpoints and
        logs. Defaults to None.
        logger (:obj:`logging.Logger`): Logger used during training.
        Defaults to None.
        meta (dict | None): A dict records some important information such as
        environment info and seed. Defaults to None.
    """

    def __init__(self,
                 conf,
                 work_dir=None,
                 logger=None,
                 meta=None):

        # check the type of `logger`
        if not isinstance(logger, logging.Logger):
            raise TypeError(f'logger must be a logging.Logger object, '
                            f'but got {type(logger)}')

        # check the type of `meta`
        if meta is not None and not isinstance(meta, dict):
            raise TypeError(
                f'meta must be a dict or None, but got {type(meta)}')

        self.conf = conf
        self.logger = logger
        self.meta = meta

        # create work_dir
        if opentool.is_str(work_dir):
            self.work_dir = osp.abspath(work_dir)
            opentool.mkdir_or_exist(self.work_dir)
        elif work_dir is None:
            self.work_dir = None
        else:
            raise TypeError('"work_dir" mus be a str or None')

        self.timestamp = get_time_str()
        self.mode = None
        self._epoch = 0
        self._step = 0
        self._inner_step = 0
        self._max_epochs = 0
        self._max_steps = 0
        self.writer = SummaryWriter(work_dir)
        self._device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    @property
    def epoch(self):
        """int: Current epoch."""
        return self._epoch

    @property
    def step(self):
        """int: Current iteration."""
        return self._step

    @property
    def inner_step(self):
        """int: Iteration in an epoch."""
        return self._inner_step

    @property
    def max_epochs(self):
        """int: Maximum training epochs."""
        return self._max_epochs

    @property
    def max_steps(self):
        """int: Maximum training iterations."""
        return self._max_steps

    @property
    def device(self):
        """tensor: cuda or cpu"""
        return self._device

    @abstractmethod
    def init(self):
        raise NotImplementedError

    @abstractmethod
    def train(self):
        raise NotImplementedError

    @abstractmethod
    def val(self):
        raise NotImplementedError

    @abstractmethod
    def save_checkpoint(self,
                        out_dir,
                        filename_tmpl,
                        save_optimizer=True,
                        meta=None):
        raise NotImplementedError

    def load_checkpoint(self, filename):
        self.logger.info('load checkpoint from %s', filename)
        return load_checkpoint(filename, self.logger)
