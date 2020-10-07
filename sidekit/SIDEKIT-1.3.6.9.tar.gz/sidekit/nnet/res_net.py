# -*- coding: utf-8 -*-
#
# This file is part of SIDEKIT.
#
# SIDEKIT is a python package for speaker verification.
# Home page: http://www-lium.univ-lemans.fr/sidekit/
#
# SIDEKIT is a python package for speaker verification.
# Home page: http://www-lium.univ-lemans.fr/sidekit/
#
# SIDEKIT is free software: you can redistribute it and/or modify
# it under the terms of the GNU LLesser General Public License as
# published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# SIDEKIT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with SIDEKIT.  If not, see <http://www.gnu.org/licenses/>.

"""
Copyright 2014-2020 Anthony Larcher
"""

import h5py
import logging
import sys
import numpy
import pickle
import torch
import torch.optim as optim
import torch.multiprocessing as mp
from torchvision import transforms
from collections import OrderedDict
from .xsets import XvectorMultiDataset, XvectorDataset, StatDataset, VoxDataset
from .xsets import FrequencyMask, CMVN, TemporalMask
from .sincnet import SincNet, SincConv1d
from ..bosaris import IdMap
from ..statserver import StatServer
from torch.utils.data import DataLoader


class FeatureMapScaling(torch.nn.Module):
    """

    """
    def __init__(self, nb_dim, do_add = True, do_mul = True):
        """

        :param nb_dim:
        :param do_add:
        :param do_mul:
        """
        super(FeatureMapScaling, self).__init__()
        self.fc = torch.nn.Linear(nb_dim, nb_dim)
        self.sig = torch.nn.Sigmoid()
        self.do_add = do_add
        self.do_mul = do_mul

    def forward(self, x):
        """

        :param x:
        :return:
        """
        y = torch.nn.functional.adaptive_avg_pool1d(x, 1).view(x.size(0), -1)
        y = self.sig(self.fc(y)).view(x.size(0), x.size(1), -1)

        if self.do_mul:
            x = x * y

        if self.do_add:
            x = x + y

        return x


class ResBlockWFMS(torch.nn.Module):
    """

    """
    def __init__(self, nb_filts, first=False):
        """

        :param nb_filts:
        :param first:
        """
        super(ResBlockWFMS, self).__init__()
        self.first = first

        if not self.first:
            self.bn1 = torch.nn.BatchNorm1d(num_features=nb_filts[0])

        self.lrelu = torch.nn.LeakyReLU()
        self.lrelu_keras = torch.nn.LeakyReLU(negative_slope=0.3)

        self.conv1 = torch.nn.Conv1d(in_channels=nb_filts[0],
                                     out_channels=nb_filts[1],
                                     kernel_size=3,
                                     padding=1,
                                     stride=1)

        self.bn2 = torch.nn.BatchNorm1d(num_features=nb_filts[1])

        self.conv2 = torch.nn.Conv1d(in_channels=nb_filts[1],
                                     out_channels=nb_filts[1],
                                     padding=1,
                                     kernel_size=3,
                                     stride=1)

        if nb_filts[0] != nb_filts[1]:
            self.downsample = True
            self.conv_downsample = torch.nn.Conv1d(in_channels=nb_filts[0],
                                                   out_channels=nb_filts[1],
                                                   padding=0,
                                                   kernel_size=1,
                                                   stride=1)
        else:
            self.downsample = False

        self.mp = torch.nn.MaxPool1d(3)

        self.fms = FeatureMapScaling(nb_dim=nb_filts[1],
                                     do_add=True,
                                     do_mul=True
                                     )

    def forward(self, x):
        """

        :param x:
        :return:
        """
        identity = x

        if not self.first:
            out = self.bn1(x)
            out = self.lrelu_keras(out)
        else:
            out = x

        #out = self.conv1(x)
        out = self.conv1(out)   # modif Anthony
        out = self.bn2(out)
        out = self.lrelu_keras(out)
        out = self.conv2(out)

        if self.downsample:
            identity = self.conv_downsample(identity)

        out += identity
        out = self.mp(out)
        out = self.fms(out)

        return out


class LayerNorm(torch.nn.Module):
    """

    """
    def __init__(self, features, eps=1e-6):
        """

        :param features:
        :param eps:
        """
        super(LayerNorm,self).__init__()
        self.gamma = torch.nn.Parameter(torch.ones(features))
        self.beta = torch.nn.Parameter(torch.zeros(features))
        self.eps = eps

    def forward(self, x):
        """

        :param x:
        :return:
        """
        mean = x.mean(-1, keepdim=True)
        std = x.std(-1, keepdim=True)
        return self.gamma * (x - mean) / (std + self.eps) + self.beta


class RawPreprocessor(torch.nn.Module):
    """

    """
    def __init__(self, nb_samp, in_channels, out_channels, kernel_size, stride=1, padding=0, dilation=1, bias=False, groups=1, min_low_hz=50, min_band_hz=50, sample_rate=16000):
        """

        :param nb_samp:
        :param in_channels:
        :param filts:
        :param first_conv:
        """
        super(RawPreprocessor, self).__init__()
        self.ln = LayerNorm(nb_samp)
        self.first_conv = SincConv1d(in_channels = in_channels,
                                     out_channels = out_channels,
                                     kernel_size = kernel_size,
                                     sample_rate = sample_rate,
                                     stride=stride,
                                     padding=padding,
                                     dilation=dilation,
                                     bias=bias,
                                     groups=groups,
                                     min_low_hz=min_low_hz,
                                     min_band_hz=min_band_hz
                                     )
        self.first_bn = torch.nn.BatchNorm1d(num_features = out_channels)
        self.lrelu = torch.nn.LeakyReLU()
        self.lrelu_keras = torch.nn.LeakyReLU(negative_slope = 0.3)

    def forward(self, x):
        """

        :param x:
        :return:
        """
        nb_samp = x.shape[0]
        len_seq = x.shape[1]
        out = self.ln(x)
        out = out.view(nb_samp, 1, len_seq)
        out = torch.nn.functional.max_pool1d(torch.abs(self.first_conv(out)), 3)
        out = self.first_bn(out)
        out = self.lrelu_keras(out)

        return out










class ResBlock(torch.nn.Module):
    """

    """
    def __init__(self, in_channels, out_channels, is_first=False):
        """

        :param filter_size:
        :param channel_nb:
        :param is_first: boolean, True if this block ios the first of the model, if not, apply a BatchNorm layer first
        """
        super(ResBlock, self).__init__()
        self.is_first = is_first
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.expansion = self.out_channels // self.in_channels

        self.resample = None
        if not self.in_channels == self.out_channels:
            self.resample = torch.nn.Sequential(
                torch.nn.Conv2d(in_channels=self.in_channels,
                                out_channels=self.out_channels,
                                kernel_size=1),
                torch.nn.BatchNorm2d(self.in_channels * self.expansion),
            )

        if not self.is_first:
            self.batch_norm1 = torch.nn.BatchNorm2d(num_features=self.in_channels)

        self.activation = torch.nn.LeakyReLU()

        self.conv1 = torch.nn.Conv2d(in_channels=self.in_channels,
                                     out_channels=self.out_channels,
                                     kernel_size=(3,3),
                                     padding=1,
                                     padding_mode='zeros',
                                     dilation=1)
        self.conv2= torch.nn.Conv2d(in_channels=self.out_channels,
                                    out_channels=self.out_channels,
                                    kernel_size=(3,3),
                                    padding=1,
                                    padding_mode='zeros',
                                    dilation=1)

        self.batch_norm2 = torch.nn.BatchNorm2d(num_features=self.out_channels)

    def forward(self, x):
        """

        :param x:
        :return:
        """
        identity = x

        if not self.is_first:
            out = self.activation(self.batch_norm1(x))
        else:
            out = x

        out = self.conv1(out)
        out = self.batch_norm2(out)
        out = self.activation(out)

        out = self.conv2(out)
        out = self.batch_norm2(out)

        if not self.expansion == 1:
            identity = self.resample(identity)
        out += identity

        out =  self.activation(out)
        return out


class ResNet18(torch.nn.Module):
    """

    """
    def __init__(self, spk_number,
                 entry_conv_kernel_size=(7,7),
                 entry_conv_out_channels=64,
                 megablock_out_channels=(64, 128, 256, 512),
                 megablock_size=(2, 2, 2, 2),
                 block_type = ResBlock
                 ):
        """

        :param spk_number:
        :param entry_conv_kernel_size:
        :param entry_conv_out_channels:
        :param megablock_out_channels:
        :param megablock_size:
        :param block_type:
        """
        super(ResNet18, self).__init__()

        self.spk_number = spk_number
        self.activation = torch.nn.LeakyReLU()

        # First convolution layer for input
        self.entry_conv = torch.nn.Conv2d(in_channels=1,
                                          out_channels=entry_conv_out_channels,
                                          kernel_size=entry_conv_kernel_size,
                                          padding=3,
                                          stride=1)
        self.entry_batch_norm = torch.nn.BatchNorm2d(entry_conv_out_channels)
        self.top_channel_number = entry_conv_out_channels

        # Add ResBlocks
        self.mega_blocks = []
        for mb_size, mb_out in zip(megablock_size, megablock_out_channels):
            self.mega_blocks.append(self._add_megablock(block_type, mb_size, mb_out))
            self.top_channel_number = mb_out

        # Top layers for classification and embeddings extraction
        self.top_lin1 = torch.nn.Linear(megablock_out_channels[-1] * 2 * 40, 512)  # a modifier pour voir la taille
        self.top_batch_norm1 = torch.nn.BatchNorm1d(512)
        self.top_lin2 = torch.nn.Linear(512, spk_number)

    def forward(self, x):
        """

        :param x:
        :return:
        """
        x = self.entry_conv(x)
        x = self.entry_batch_norm(x)
        x = self.activation(x)

        for layer in self.mega_blocks:
            x = layer(x)

        # Pooling done as for x-vectors
        mean = torch.mean(x, dim=2)
        mean = torch.flatten(mean, 1)
        std = torch.std(x, dim=2)
        std = torch.flatten(std, 1)
        x = torch.cat([mean, std], dim=1)

        # Classification layers
        x = self.top_lin1(x)
        x = self.top_batch_norm1(x)
        x = self.activation(x)
        x = self.top_lin2(x)

        return x

    def _add_megablock(self, block_type, block_nb, out_channels, is_first=False):

        rblocks = [block_type(self.top_channel_number, out_channels, is_first=is_first),]
        for _ in range(1, block_nb):
            rblocks.append(block_type(out_channels, out_channels, is_first=False))
        return torch.nn.Sequential(*rblocks)


def restrain(args):
    """
    Initialize and train an ResNet for Speaker Recognition

    :param args:
    :return:
    """
    # Initialize a first model and save to disk
    model = ResNet18(args.class_number,
                     entry_conv_kernel_size=(7,7),
                     entry_conv_out_channels=64,
                     megablock_out_channels=(64, 128, 128, 128),
                     megablock_size=(2, 2, 2, 2),
                     block_type = ResBlock)

    current_model_file_name = "initial_model"
    torch.save(model.state_dict(), current_model_file_name)

    for epoch in range(1, args.epochs + 1):
        current_model_file_name = train_resnet_epoch(epoch, args, current_model_file_name)

        # Add the cross validation here
        accuracy = resnet_cross_validation(args, current_model_file_name)
        print("*** Cross validation accuracy = {} %".format(accuracy))

        # Decrease learning rate after every epoch
        args.lr = args.lr * 0.9
        print("        Decrease learning rate: {}".format(args.lr))


def train_resnet_epoch(model, epoch, train_seg_df, speaker_dict, args):
    """

    :param model:
    :param epoch:
    :param train_seg_df:
    :param args:
    :return:
    """
    device = torch.device("cuda:0")

    torch.manual_seed(args.seed)

    train_transform = []
    if not args.train_transformation == '':
        trans = args.train_transformation.split(',')
        for t in trans:
            if "CMVN" in t:
                train_transform.append(CMVN())
            if "FrequencyMask" in t:
                a = t.split(",")[0].split("(")[1]
                b = t.split(",")[1].split("(")[0]
                train_transform.append(FrequencyMask(a, b))
            if "TemporalMask" in t:
                a = t.split(",")[0].split("(")[1]
                train_transform.append(TemporalMask(a, b))
    train_set = VoxDataset(train_seg_df, speaker_dict, 500, transform=transforms.Compose(train_transform),
                           spec_aug_ratio=args.spec_aug, temp_aug_ratio=args.temp_aug)
    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True, num_workers=15)

    optimizer = torch.optim.Adam(model.parameters())
    criterion = torch.nn.CrossEntropyLoss()

    accuracy = 0.0
    for batch_idx, (data, target, _, __) in enumerate(train_loader):
        target = target.squeeze()
        optimizer.zero_grad()
        output = model(data.to(device))
        loss = criterion(output, target.to(device))
        loss.backward()
        optimizer.step()
        accuracy += (torch.argmax(output.data, 1) == target.to(device)).sum()

        if batch_idx % args.log_interval == 0:
            logging.critical('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}\tAccuracy: {:.3f}'.format(
                epoch, batch_idx + 1, train_loader.__len__(),
                       100. * batch_idx / train_loader.__len__(), loss.item(),
                       100.0 * accuracy.item() / ((batch_idx + 1) * args.batch_size)))
    return model

def resnet_cross_validation(args, model, cv_seg_df, speaker_dict):
    """

    :param args:
    :param model:
    :param cv_seg_df:
    :return:
    """
    cv_transform = []
    if not args.cv_transformation == '':
        trans = args.cv_transformation.split(',')
        for t in trans:
            if "CMVN" in t:
                cv_transform.append(CMVN())
            if "FrequencyMask" in t:
                a = t.split(",")[0].split("(")[1]
                b = t.split(",")[1].split("(")[0]
                cv_transform.append(FrequencyMask(a, b))
            if "TemporalMask" in t:
                a = t.split(",")[0].split("(")[1]
                cv_transform.append(TemporalMask(a, b))
    cv_set = VoxDataset(cv_seg_df, speaker_dict, 500, transform=transforms.Compose(cv_transform),
                        spec_aug_ratio=args.spec_aug, temp_aug_ratio=args.temp_aug)
    cv_loader = DataLoader(cv_set, batch_size=args.batch_size, shuffle=False, num_workers=15)
    model.eval()
    device = torch.device("cuda:0")
    model.to(device)

    accuracy = 0.0
    print(cv_set.__len__())
    for batch_idx, (data, target, _, __) in enumerate(cv_loader):
        target = target.squeeze()
        output = model(data.to(device))
        accuracy += (torch.argmax(output.data, 1) == target.to(device)).sum()
    return 100. * accuracy.cpu().numpy() / ((batch_idx + 1) * args.batch_size)
