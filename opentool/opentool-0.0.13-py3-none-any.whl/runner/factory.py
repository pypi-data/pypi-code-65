import torch.nn as nn
from torchvision import transforms as T


def get_transforms(transforms):
    if not isinstance(transforms, list):
        raise TypeError('Expected list but type {} was passed!'.
                        format(type(transforms)))

    def get_object(transform):
        if hasattr(T, transform.type):
            return getattr(T, transform.type)
        else:
            return eval(transform.type)
    transforms = [get_object(transform)(**transform.params)
                  for transform in transforms]
    return T.Compose(transforms)


def get_criterion(criterion):
    criterion = getattr(nn, criterion.type)(**criterion.params)
    return criterion


def get_optimizer(optimizer, model):
    pass
