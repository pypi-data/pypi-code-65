# -*- coding: utf-8 -*-
#
# This file is part of s4d.
#
# s4d is a python package for speaker diarization.
# Home page: http://www-lium.univ-lemans.fr/s4d/
#
# s4d is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# s4d is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with s4d.  If not, see <http://www.gnu.org/licenses/>.


"""
Copyright 2014-2020 Anthony Larcher
"""

import os
import sys
import logging
import pandas
import numpy
from collections import OrderedDict
import random
import h5py
import shutil
import torch
import torch.nn as nn
import yaml

from torch import optim
from torch.utils.data import Dataset

from .wavsets import SeqSet
from sidekit.nnet.sincnet import SincNet
from torch.utils.data import DataLoader

__license__ = "LGPL"
__author__ = "Anthony Larcher"
__copyright__ = "Copyright 2015-2020 Anthony Larcher"
__maintainer__ = "Anthony Larcher"
__email__ = "anthony.larcher@univ-lemans.fr"
__status__ = "Production"
__docformat__ = 'reS'


# def save_checkpoint(state, is_best, filename='checkpoint.pth.tar', best_filename='model_best.pth.tar'):
#     """
#
#     :param state:
#     :param is_best:
#     :param filename:
#     :param best_filename:
#     :return:
#     """
#     torch.save(state, filename)
#     if is_best:
#         shutil.copyfile(filename, best_filename)


class BLSTM(nn.Module):
    def __init__(self,
                 input_size,
                 blstm_sizes):
        """

        :param input_size:
        :param blstm_sizes:
        """
        super(BLSTM, self).__init__()
        self.input_size = input_size
        self.blstm_sizes = blstm_sizes
        self.blstm_layers = []

        for blstm_size in blstm_sizes:
            self.blstm_layers.append(nn.LSTM(input_size, blstm_size // 2, bidirectional=True, batch_first=True))
            input_size = blstm_size
            self.output_size = blstm_size

        self.hidden = None
    """
    Bi LSTM model used for voice activity detection or speaker turn detection
    """

    def forward(self, inputs):
        """

        :param inputs:
        :return:
        """
        #for idx, _s in enumerate(self.blstm_sizes):
        #    self.blstm_layers[idx].flatten_parameters()

        hiddens = []
        if self.hidden is None:
            #hidden_1, hidden_2 = None, None
            for _s in self.blstm_sizes:
                hiddens.append(None)
        else:
            hiddens = list(self.hidden)

        x = inputs
        outputs = []
        for idx, _s in enumerate(self.blstm_sizes):
            x, hiddens[idx] = self.blstm_layers[idx](x, hiddens[idx])
            outputs.append(x)
        self.hidden = tuple(hiddens)
        output = torch.cat(outputs, dim=2)

        return x

    def output_size(self):
        return self.output_size


class SeqToSeq(nn.Module):
    """
    Model used for voice activity detection or speaker turn detection
    This model can include a pre-processor to input raw waveform,
    a BLSTM module to process the sequence-to-sequence
    and other linear of convolutional layers
    """
    def __init__(self,
                 model_archi):

        super(SeqToSeq, self).__init__()

        # Load Yaml configuration
        with open(model_archi, 'r') as fh:
            cfg = yaml.load(fh, Loader=yaml.FullLoader)

        self.loss = cfg["loss"]
        self.feature_size = None

        """
        Prepare Preprocessor
        """
        self.preprocessor = None
        if "preprocessor" in cfg:
            if cfg['preprocessor']["type"] == "sincnet":
                self.preprocessor = SincNet(
                    waveform_normalize=cfg['preprocessor']["waveform_normalize"],
                    sample_rate=cfg['preprocessor']["sample_rate"],
                    min_low_hz=cfg['preprocessor']["min_low_hz"],
                    min_band_hz=cfg['preprocessor']["min_band_hz"],
                    out_channels=cfg['preprocessor']["out_channels"],
                    kernel_size=cfg['preprocessor']["kernel_size"],
                    stride=cfg['preprocessor']["stride"],
                    max_pool=cfg['preprocessor']["max_pool"],
                    instance_normalize=cfg['preprocessor']["instance_normalize"],
                    activation=cfg['preprocessor']["activation"],
                    dropout=cfg['preprocessor']["dropout"]
                )
                self.feature_size = self.preprocessor.dimension

        """
        Prepare sequence to sequence  network
        """
        # Get Feature size
        if self.feature_size is None:
            self.feature_size = cfg["feature_size"]

        input_size = self.feature_size

        self.sequence_to_sequence = BLSTM(input_size=input_size,
                                          blstm_sizes=cfg["sequence_to_sequence"]["blstm_sizes"])

        input_size = self.sequence_to_sequence.output_size

        """
        Prepare post-processing network
        """
        # Create sequential object for the second part of the network
        self.post_processing_activation = torch.nn.Tanh()
        post_processing_layers = []
        for k in cfg["post_processing"].keys():

            if k.startswith("lin"):
                post_processing_layers.append((k, torch.nn.Linear(input_size,
                                                                  cfg["post_processing"][k]["output"])))
                input_size = cfg["post_processing"][k]["output"]

            elif k.startswith("activation"):
                post_processing_layers.append((k, self.post_processing_activation))

            elif k.startswith('batch_norm'):
                post_processing_layers.append((k, torch.nn.BatchNorm1d(input_size)))

            elif k.startswith('dropout'):
                post_processing_layers.append((k, torch.nn.Dropout(p=cfg["post_processing"][k])))

        self.post_processing = torch.nn.Sequential(OrderedDict(post_processing_layers))
        #self.before_speaker_embedding_weight_decay = cfg["post_processing"]["weight_decay"]


    def forward(self, inputs):
        """

        :param inputs:
        :return:
        """
        if self.preprocessor is not None:
            x = self.preprocessor(inputs)
        else:
            x = inputs
        x = self.sequence_to_sequence(x)
        x = self.post_processing(x)
        return x


def seqTrain(dataset_yaml,
             model_yaml,
             mode,
             epochs=100,
             lr=0.0001,
             patience=10,
             model_name=None,
             tmp_model_name=None,
             best_model_name=None,
             multi_gpu=True,
             opt='sgd',
             filter_type="gate",
             collar_duration=0.1,
             framerate=16000,
             output_rate=100,
             batch_size=32,
             log_interval=10,
             num_thread=10
             ):
    """

    :param data_dir:
    :param mode:
    :param duration:
    :param seg_shift:
    :param filter_type:
    :param collar_duration:
    :param framerate:
    :param epochs:
    :param lr:
    :param loss:
    :param patience:
    :param tmp_model_name:
    :param best_model_name:
    :param multi_gpu:
    :param opt:
    :return:
    """
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # Start from scratch
    if model_name is None:
       model = SeqToSeq(model_yaml)
    # If we start from an existing model
    else:
        # Load the model
        logging.critical(f"*** Load model from = {model_name}")
        checkpoint = torch.load(model_name)
        model = SeqToSeq(model_yaml)

    if torch.cuda.device_count() > 1 and multi_gpu:
        print("Let's use", torch.cuda.device_count(), "GPUs!")
        model = torch.nn.DataParallel(model)
    else:
        print("Train on a single GPU")
    model.to(device)

    """
    Create two dataloaders for training and evaluation
    """
    with open(dataset_yaml, "r") as fh:
        dataset_params = yaml.load(fh, Loader=yaml.FullLoader)
        #df = pandas.read_csv(dataset_params["dataset_description"])
    #training_df, validation_df = train_test_split(df, test_size=dataset_params["validation_ratio"])

    torch.manual_seed(dataset_params['seed'])
    training_set = SeqSet(dataset_yaml,
                          wav_dir="data/wav/",
                          mdtm_dir="data/mdtm/",
                          mode="vad",
                          duration=2.,
                          filter_type="gate",
                          collar_duration=0.1,
                          audio_framerate=16000,
                          output_framerate=100,
                          transform_pipeline="MFCC")

    training_loader = DataLoader(training_set,
                                 batch_size=dataset_params["batch_size"],
                                 shuffle=True,
                                 drop_last=True,
                                 pin_memory=True,
                                 num_workers=num_thread)

    #validation_set = SeqSet(dataset_yaml,
    #                        set_type="validation",
    #                        dataset_df=validation_df)

    #validation_loader = DataLoader(validation_set,
    #                               batch_size=dataset_params["batch_size"],
    #                               drop_last=True,
    #                               pin_memory=True,
    #                               num_workers=num_thread)

    """
    Set the training options
    """
    if opt == 'sgd':
        _optimizer = torch.optim.SGD
        _options = {'lr': lr, 'momentum': 0.9}
    elif opt == 'adam':
        _optimizer = torch.optim.Adam
        _options = {'lr': lr}
    elif opt == 'rmsprop':
        _optimizer = torch.optim.RMSprop
        _options = {'lr': lr}

    params = [
        {
            'params': [
                param for name, param in model.named_parameters() if 'bn' not in name
            ]
        },
        {
            'params': [
                param for name, param in model.named_parameters() if 'bn' in name
            ],
            'weight_decay': 0
        },
    ]

    optimizer = _optimizer([{'params': model.parameters()},], **_options)
    #if type(model) is SeqToSeq:
    #    optimizer = _optimizer([
    #        {'params': model.parameters(),
    #         'weight_decay': model.weight_decay},],
    #        **_options
    #    )
    #else:
    #    optimizer = _optimizer([
    #        {'params': model.module.sequence_network.parameters(),
    #         #'weight_decay': model.module.sequence_network_weight_decay},],
    #        **_options
    #    )

    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', verbose=True)

    best_accuracy = 0.0
    best_accuracy_epoch = 1
    curr_patience = patience
    for epoch in range(1, epochs + 1):
        # Process one epoch and return the current model
        if curr_patience == 0:
            print(f"Stopping at epoch {epoch} for cause of patience")
            break
        model = train_epoch(model,
                            epoch,
                            training_loader,
                            optimizer,
                            log_interval,
                            device=device)

        # Cross validation here
        #accuracy, val_loss = cross_validation(model, validation_loader, device=device)
        #logging.critical("*** Cross validation accuracy = {} %".format(accuracy))

        # Decrease learning rate according to the scheduler policy
        #scheduler.step(val_loss)
        #print(f"Learning rate is {optimizer.param_groups[0]['lr']}")

        # remember best accuracy and save checkpoint
        #is_best = accuracy > best_accuracy
        #best_accuracy = max(accuracy, best_accuracy)

        #if type(model) is SeqToSeq:
        #    save_checkpoint({
        #        'epoch': epoch,
        #        'model_state_dict': model.state_dict(),
        #        'optimizer_state_dict': optimizer.state_dict(),
        #        'accuracy': best_accuracy,
        #        'scheduler': scheduler
        #    }, is_best, filename=tmp_model_name + ".pt", best_filename=best_model_name + '.pt')
        #else:
        #    save_checkpoint({
        #        'epoch': epoch,
        #        'model_state_dict': model.module.state_dict(),
        #        'optimizer_state_dict': optimizer.state_dict(),
        #        'accuracy': best_accuracy,
        #        'scheduler': scheduler
        #    }, is_best, filename=tmp_model_name + ".pt", best_filename=best_model_name + '.pt')

        #if is_best:
        #    best_accuracy_epoch = epoch
        #    curr_patience = patience
        #else:
        #    curr_patience -= 1

    #logging.critical(f"Best accuracy {best_accuracy * 100.} obtained at epoch {best_accuracy_epoch}")


def train_epoch(model, epoch, training_loader, optimizer, log_interval, device):
    """

    :param model:
    :param epoch:
    :param training_loader:
    :param optimizer:
    :param log_interval:
    :param device:
    :param clipping:
    :return:
    """
    model.to(device)
    model.train()
    criterion = torch.nn.CrossEntropyLoss(reduction='mean')

    accuracy = 0.0
    for batch_idx, (data, target) in enumerate(training_loader):
        target = target.squeeze()
        optimizer.zero_grad()
        output = model(data.to(device))
        output = output.permute(1, 2, 0)
        target = target.permute(1, 0)

        loss = criterion(output, target.to(device))
        loss.backward(retain_graph=True)
        optimizer.step()
        accuracy += (torch.argmax(output.data, 1) == target.to(device)).sum()

        if batch_idx % log_interval == 0:
            batch_size = target.shape[0]
            logging.critical('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}\tAccuracy: {:.3f}'.format(
                epoch, batch_idx + 1, training_loader.__len__(),
                100. * batch_idx / training_loader.__len__(), loss.item(),
                100.0 * accuracy.item() / ((batch_idx + 1) * batch_size * 198)))
    return model


def cross_validation(model, validation_loader, device):
    """

    :param model:
    :param validation_loader:
    :param device:
    :return:
    """
    model.eval()

    accuracy = 0.0
    loss = 0.0
    criterion = torch.nn.CrossEntropyLoss()
    with torch.no_grad():
        for batch_idx, (data, target) in enumerate(validation_loader):
            batch_size = target.shape[0]
            target = target.squeeze()
            output = model(data.to(device),target=target.to(device),is_eval=True)
            print(output.shape)
            accuracy += (torch.argmax(output.data, 1) == target.to(device)).sum()

            loss += criterion(output, target.to(device))
    return 100. * accuracy.cpu().numpy() / ((batch_idx + 1) * batch_size), \
           loss.cpu().numpy() / ((batch_idx + 1) * batch_size)

