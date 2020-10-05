# Loss functions used for training GANs
# Author: Xiao Li

from typing import Union, Callable

import torch
import torch.nn as nn
import torch.autograd as autograd
import torch.nn.functional as F


class GANLossMixIn:
    r"""
    Loss function for training GANs.
    This class is a MixIn class;
    To use it in you project, inherit from this class
    as well as nn.Module.
    """

    # Non-saturated logistic loss for G
    def G_logistic_ns(self, fake_data: torch.Tensor,
                      d_callable: Union[Callable, nn.Module]):
        fake_d = d_callable(fake_data)
        return F.softplus(-fake_d).mean()

    # WGAN loss for G
    def G_wgan(self, fake_data: torch.Tensor,
               d_callable: Union[Callable, nn.Module]):
        fake_d = d_callable(fake_data)
        return -fake_d.mean()

    # logistic loss for D.
    def D_logistic(self, real_d: torch.Tensor, fake_d: torch.Tensor):
        return F.softplus(fake_d).mean() + F.softplus(-real_d).mean()

    # Hinge loss for D.
    def D_hinge(self, real_d: torch.Tensor, fake_d: torch.Tensor):
        loss = (F.relu(1. + real_d) + F.relu(1. - fake_d))
        return loss.mean()

    # WGAN loss for D.
    def D_wgan(self, real_d: torch.Tensor, fake_d: torch.Tensor):
        loss = fake_d - real_d
        return loss.mean()

    # Gradient Penalty for D.
    def D_gp(self, fake_data: torch.Tensor, real_data: torch.Tensor,
             d_callable: Union[Callable, nn.Module]):
        real_data.requires_grad = True
        _rnd = torch.randn(real_data.shape[0], 1, 1, 1, device=real_data.device)

        mix_data = torch.lerp(fake_data.detach(), real_data, _rnd)
        mix_d = d_callable(mix_data)
        mix_grad = autograd.grad(mix_d.sum(), mix_data, create_graph=True)[0]
        grad_norm = torch.sqrt(torch.sum(torch.square(mix_grad.view(mix_grad.shape[0], -1)), dim=-1, keepdim=True))
        loss = torch.square(grad_norm - 1.)

        return loss.mean()
