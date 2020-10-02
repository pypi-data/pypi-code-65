import os

from bentoml.exceptions import (
    InvalidArgument,
    MissingDependencyException,
)
from bentoml.service import BentoServiceArtifact
import torch

try:
    from simpletransformers.classification import MultiLabelClassificationModel
except ImportError:
    MultiLabelClassificationModel = None


class SimpleTransformersModelArtifact(BentoServiceArtifact):

    def __init__(self,
        name,
        model_type='roberta',
        num_labels=None,
        pos_weight=None,
        args=None,
        use_cuda=False,
        cuda_device=-1,
        **kwargs
    ):
        super(SimpleTransformersModelArtifact, self).__init__(name)
        self._model = None
        self._model_type = model_type
        self._num_labels = num_labels
        self._pos_weight = pos_weight
        self._args = args
        self._use_cuda = use_cuda
        self._cuda_device = cuda_device
        self._kwargs = kwargs

        if MultiLabelClassificationModel is None:
            raise MissingDependencyException(
                'simpletransformers.classification.MultiLabelClassificationModel is required to use SimpleTransformersModelArtifact'
            )

    def _file_path(self, base_path):
        return os.path.join(base_path, self.name)

    def _load_from_directory(self, path):
        self._model = MultiLabelClassificationModel(
            self._model_type,
            self._file_path(path),
            num_labels=self._num_labels,
            pos_weight=self._pos_weight,
            args=self._args,
            use_cuda=self._use_cuda,
            cuda_device=self._cuda_device,
            **self._kwargs
        )
    
    def pack(self, model):
        if isinstance(model, str):
            if os.path.isdir(model):
                self._load_from_directory(model)
                return self
        
        raise InvalidArgument('Expecting a path to the model directory')


    def load(self, path):
        return self.pack(path)

    def save(self, dst):
        path = self._file_path(dst)
        os.makedirs(path, exist_ok=True)
        model = self._model.model
        model_to_save = model.module if hasattr(model, 'module') else model
        model_to_save.save_pretrained(path)
        self._model.tokenizer.save_pretrained(path)
        torch.save(self._model.args, os.path.join(path, 'training_args.bin'))
        return path

    def get(self):
        return self._model
