# -*- coding: UTF-8 -*-
""""
Created on 20.02.20
Module with model performing attention pooling.

:author:     Martin Dočekal
"""

import torch
from typing import Optional


class AttentionPooler(torch.nn.Module):
    """
    Module performing attention pooling.

    The attention implementation is inspired from the:
        Neural Machine Translation by Jointly Learning to Align and Translate
            Dzmitry Bahdanau, Kyunghyun Cho, Yoshua Bengio
            https://arxiv.org/abs/1409.0473
    """

    def __init__(self, inputSize: int, hiddenStateSize: Optional[int] = None):
        """
        Initialization of attention pooler.

        :param inputSize: Number of dimensions of one element from input sequence.
        :type inputSize: int
        :param hiddenStateSize: Optional parameter determining number of dimensions of the hidden state. By the hidden
            state we mean the previous hidden state s_(i-1) of the rnn from the paper https://arxiv.org/abs/1409.0473 that goes
            to the input of this module.
            Of course if you do not use the RNNs you can just pass any vector you want.

            By default it is the same as inputSize.
        :type hiddenStateSize: Optional[int]
        """
        super().__init__()

        self.inputSize = inputSize
        self.hiddenStateSize = inputSize if hiddenStateSize is None else hiddenStateSize

        self._a = torch.nn.Linear(self.hiddenStateSize+self.inputSize, 1)
        self._softMax = torch.nn.Softmax(dim=1)

    def forward(self, hiddenState: torch.Tensor, sequence: torch.Tensor, attentionMask: Optional[torch.Tensor] = None, toPooling: torch.Tensor = None) -> torch.Tensor:
        """
        Performs attention based pooling of given sequence and given hidden state.

        :param hiddenState: By the hidden state we mean the previous hidden state s_(i-1) of the rnn from the paper
            https://arxiv.org/abs/1409.0473 that goes to the input of this module.
            Of course if you do not use the RNNs you can just pass any vector you want.

            Size BATCH x self.hiddenStateSize
        :type hiddenState: torch.Tensor
        :param sequence: Sequence of elements you want to perform the pooling on.
            Size BATCH x SIZE OF SEQUENCE x self.inputSize
        :type sequence: torch.Tensor
        :param attentionMask: Mask out elements of the sequence. 0 means mask out.
            Size BATCH x SIZE OF SEQUENCE
        :type attentionMask: Optional[torch.Tensor]
        :param toPooling: Use this parameter when you want to calculate attention score according to sequence, but you want to
            pool different values than the sequence itself.
            Size BATCH x SIZE OF SEQUENCE x ANYTHING
        :type toPooling: Optional[torch.Tensor]
        :return: Pooled vector.
            Size BATCH x self.inputSize (or toPooling size)
        :rtype: torch.Tensor
        """

        if attentionMask is None:
            attentionMask = torch.ones(sequence.shape[:2], device=sequence.device)
        else:
            # convert zeroes to some big negative value to mask out during the softmax
            # This mask will be added to the real score and because the e^-inf is zero we are getting close to the wanted zero.

            attentionMask = (1.0-attentionMask)*(-10000.0)

        if toPooling is None:
            toPooling = sequence

        # concatenate hidden state to each sequence element
        C = torch.cat((hiddenState.unsqueeze(dim=1).expand(hiddenState.shape[0], sequence.shape[1], hiddenState.shape[1]), sequence), dim=2)

        # Linear transformation of the sequence of elements in context of given hidden state to get the scores.
        s = self._a(C)

        # Add -info to the scores of elements i want to mask out.
        s += attentionMask.unsqueeze(dim=2)

        # Calculating probabilities from the scores.
        p = self._softMax(s)

        # Weight (score) base pooling
        return torch.sum(p*toPooling, dim=1)

