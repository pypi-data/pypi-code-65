# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Base model factory class to be used by object detection and classification"""

from abc import ABC, abstractmethod


class BaseModelFactory(ABC):
    """Base class defining interface to be used by object detection and classification model factories"""

    @classmethod
    @abstractmethod
    def download_model_weights(cls, model_name):
        """ Download model weights to a predefined location for a model.
        These weights will be later used to setup model wrapper.

        :param model_name: string name of the model
        :type model_name: str
        """
        pass
