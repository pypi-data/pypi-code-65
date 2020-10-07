# coding: utf-8 -*-
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
Copyright 2014-2020 Yevhenii Prokopalo, Anthony Larcher
"""


import pdb
import traceback
import logging
import matplotlib.pyplot as plt
import multiprocessing
import numpy
import pandas
import pickle
import shutil
import time
import torch
import torch.optim as optim
import yaml

from torchvision import transforms
from collections import OrderedDict
from .xsets import SideSet
from .xsets import IdMapSet
from .res_net import RawPreprocessor, ResBlockWFMS
from ..bosaris import IdMap
from ..statserver import StatServer
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from .sincnet import SincNet
#from torch.utils.tensorboard import SummaryWriter
from .loss import ArcLinear

import tqdm

__license__ = "LGPL"
__author__ = "Anthony Larcher"
__copyright__ = "Copyright 2015-2020 Anthony Larcher"
__maintainer__ = "Anthony Larcher"
__email__ = "anthony.larcher@univ-lemans.fr"
__status__ = "Production"
__docformat__ = 'reS'


logging.basicConfig(format='%(asctime)s %(message)s')


# Make PyTorch Deterministic
torch.manual_seed(0)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
numpy.random.seed(0)


class GuruMeditation (torch.autograd.detect_anomaly):
    
    def __init__(self):
        super(GuruMeditation, self).__init__()

    def __enter__(self):
        super(GuruMeditation, self).__enter__()
        return self

    def __exit__(self, type, value, trace):
        super(GuruMeditation, self).__exit__()
        if isinstance(value, RuntimeError):
            traceback.print_tb(trace)
            halt(str(value))

    def halt(msg):
        print (msg)
        pdb.set_trace()









def select_n_random(data, labels, n=100):
    '''
    Selects n random datapoints and their corresponding labels from a dataset
    '''
    assert len(data) == len(labels)

    perm = torch.randperm(len(data))
    return data[perm][:n], labels[perm][:n]


def matplotlib_imshow(img, one_channel=False):
    if one_channel:
        img = img.mean(dim=0)
    img = img / 2 + 0.5     # unnormalize
    npimg = img.cpu().numpy()
    if one_channel:
        plt.imshow(npimg, cmap="Greys")
    else:
        plt.imshow(np.transpose(npimg, (1, 2, 0)))

def speech_to_probs(model, speech):
    '''
    Generates predictions and corresponding probabilities from a trained
    network and a list of images
    '''
    output = model(speech)
    # convert output probabilities to predicted class
    _, preds_tensor = torch.max(output, 1)
    preds = numpy.squeeze(preds_tensor.cpu().numpy())
    return preds, [torch.nn.functional.softmax(el, dim=0)[i].item() for i, el in zip(preds, output)]


def plot_classes_preds(model, speech, labels):
    '''

    Generates matplotlib Figure using a trained network, along with images
    and labels from a batch, that shows the network's top prediction along
    with its probability, alongside the actual label, coloring this
    information based on whether the prediction was correct or not.
    Uses the "speech_to_probs" function.
    '''
    preds, probs = speech_to_probs(model, speech)
    # plot the images in the batch, along with predicted and true labels
    fig = plt.figure(figsize=(12, 48))
    for idx in numpy.arange(4):
         ax = fig.add_subplot(1, 4, idx+1, xticks=[], yticks=[])
         #matplotlib_imshow(speech[idx], one_channel=True)
         ax.set_title("{0}, {1:.1f}%\n(label: {2})".format(
                                                           preds[idx],
                                                           probs[idx] * 100.0,
                                                           labels[idx]),
                                                           color=("green" if preds[idx]==labels[idx].item() else "red"))
    return fig



def get_lr(optimizer):
    """

    :param optimizer:
    :return:
    """
    for param_group in optimizer.param_groups:
        return param_group['lr']


def save_checkpoint(state, is_best, filename='checkpoint.pth.tar', best_filename='model_best.pth.tar'):
    """

    :param state:
    :param is_best:
    :param filename:
    :param best_filename:
    :return:
    """
    torch.save(state, filename)
    if is_best:
        shutil.copyfile(filename, best_filename)

class MeanStdPooling(torch.nn.Module):
    """
    Mean and Standard deviation pooling
    """
    def __init__(self):
        """

        """
        super(MeanStdPooling, self).__init__()
        pass

    def forward(self, x):
        """

        :param x:
        :return:
        """
        mean = torch.mean(x, dim=2)
        std = torch.std(x, dim=2)
        return torch.cat([mean, std], dim=1)


class GruPooling(torch.nn.Module):
    """

    """
    def __init__(self, input_size, gru_node, nb_gru_layer):
        """

        :param input_size:
        :param gru_node:
        :param nb_gru_layer:
        """
        super(GruPooling, self).__init__()
        self.lrelu_keras = torch.nn.LeakyReLU(negative_slope = 0.3)
        self.bn_before_gru = torch.nn.BatchNorm1d(num_features = input_size)
        self.gru = torch.nn.GRU(input_size = input_size,
                          hidden_size = gru_node,
                          num_layers = nb_gru_layer,
                          batch_first = True)

    def forward(self, x):
        """

        :param x:
        :return:
        """
        x = self.bn_before_gru(x)
        x = self.lrelu_keras(x)
        x = x.permute(0, 2, 1)  #(batch, filt, time) >> (batch, time, filt)
        self.gru.flatten_parameters()
        x, _ = self.gru(x)
        x = x[:,-1,:]

        return x


class Xtractor(torch.nn.Module):
    """
    Class that defines an x-vector extractor based on 5 convolutional layers and a mean standard deviation pooling
    """

    def __init__(self,
                 speaker_number,
                 model_archi="xvector",
                 loss=None,
                 norm_embedding=False,
                 aam_margin=0.5,
                 aam_s=0.5):
        """
        If config is None, default architecture is created
        :param model_archi:
        """
        super(Xtractor, self).__init__()
        self.speaker_number = speaker_number
        self.feature_size = None
        self.norm_embedding = norm_embedding

        if model_archi == "xvector":

            if loss not in ["cce", 'aam']:
                raise NotImplementedError(f"The valid loss are for now cce and aam ")
            else:
                self.loss = loss

            self.feature_size = 30
            self.activation = torch.nn.LeakyReLU(0.2)

            self.preprocessor = None

            self.sequence_network = torch.nn.Sequential(OrderedDict([
                ("conv1", torch.nn.Conv1d(self.feature_size, 512, 5, dilation=1)),
                ("activation1", torch.nn.LeakyReLU(0.2)),
                ("batch_norm1", torch.nn.BatchNorm1d(512)),
                ("conv2", torch.nn.Conv1d(512, 512, 3, dilation=2)),
                ("activation2", torch.nn.LeakyReLU(0.2)),
                ("batch_norm2", torch.nn.BatchNorm1d(512)),
                ("conv3", torch.nn.Conv1d(512, 512, 3, dilation=3)),
                ("activation3", torch.nn.LeakyReLU(0.2)),
                ("batch_norm3", torch.nn.BatchNorm1d(512)),
                ("conv4", torch.nn.Conv1d(512, 512, 1)),
                ("activation4", torch.nn.LeakyReLU(0.2)),
                ("batch_norm4", torch.nn.BatchNorm1d(512)),
                ("conv5", torch.nn.Conv1d(512, 1536, 1)),
                ("activation5", torch.nn.LeakyReLU(0.2)),
                ("batch_norm5", torch.nn.BatchNorm1d(1536))
            ]))

            self.stat_pooling = MeanStdPooling()

            self.before_speaker_embedding = torch.nn.Sequential(OrderedDict([
                ("linear6", torch.nn.Linear(3072, 512))
            ]))

            if self.loss == "aam":
                self.after_speaker_embedding = torch.nn.Sequential(OrderedDict([
                  ("arclinear", ArcLinear(512, int(self.speaker_number), margin=aam_margin, s=aam_s))
                ]))
            elif self.loss == "cce":
                self.after_speaker_embedding = torch.nn.Sequential(OrderedDict([
                    ("activation6", torch.nn.LeakyReLU(0.2)),
                    ("batch_norm6", torch.nn.BatchNorm1d(512)),
                    ("dropout6", torch.nn.Dropout(p=0.05)),
                    ("linear7", torch.nn.Linear(512, 512)),
                    ("activation7", torch.nn.LeakyReLU(0.2)),
                    ("batch_norm7", torch.nn.BatchNorm1d(512)),
                    ("linear8", torch.nn.Linear(512, int(self.speaker_number)))
                ]))

            self.sequence_network_weight_decay = 0.0002
            self.before_speaker_embedding_weight_decay = 0.002
            self.after_speaker_embedding_weight_decay = 0.002

        elif model_archi == "rawnet2":

            if loss not in ["cce", 'aam']:
                raise NotImplementedError(f"The valid loss are for now cce and aam ")
            else:
                self.loss = loss

            filts = [128, [128, 128], [128, 256], [256, 256]]
            self.norm_embedding = True

            self.preprocessor = RawPreprocessor(nb_samp=48000,
                                                in_channels=1,
                                                out_channels=filts[0],
                                                kernel_size=3)

            self.sequence_network = torch.nn.Sequential(OrderedDict([
                ("block0", ResBlockWFMS(nb_filts=filts[1], first=True)),
                ("block1", ResBlockWFMS(nb_filts=filts[1])),
                ("block2", ResBlockWFMS(nb_filts=filts[2])),
                ("block3", ResBlockWFMS(nb_filts=[filts[2][1], filts[2][1]])),
                ("block4", ResBlockWFMS(nb_filts=[filts[2][1], filts[2][1]])),
                ("block5", ResBlockWFMS(nb_filts=[filts[2][1], filts[2][1]]))
            ]))

            self.stat_pooling = GruPooling(input_size=filts[2][-1],
                                           gru_node=1024,
                                           nb_gru_layer=1)

            self.before_speaker_embedding = torch.nn.Linear(in_features = 1024,
                                                            out_features = 1024)

            if self.loss == "aam":
                if loss == 'aam':
                    self.after_speaker_embedding = ArcLinear(1024,
                                                             int(self.speaker_number),
                                                             margin=aam_margin, s=aam_s)
            elif self.loss == "cce":
                self.after_speaker_embedding = torch.nn.Linear(in_features = 1024,
                                                               out_features = int(self.speaker_number),
                                                               bias = True)

            self.preprocessor_weight_decay = 0.000
            self.sequence_network_weight_decay = 0.000
            self.stat_pooling_weight_decay = 0.000
            self.before_speaker_embedding_weight_decay = 0.00
            self.after_speaker_embedding_weight_decay = 0.00

        else:
            if isinstance(model_archi, dict):
                cfg = model_archi
            else:
                # Load Yaml configuration
                with open(model_archi, 'r') as fh:
                    cfg = yaml.load(fh, Loader=yaml.FullLoader)

            self.loss = cfg["training"]["loss"]
            if self.loss == "aam":
                self.aam_margin = cfg["training"]["aam_margin"]
                self.aam_s = cfg["training"]["aam_s"]

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
                elif cfg['preprocessor']["type"] == "rawnet2":
                    self.preprocessor = RawPreprocessor(nb_samp=int(cfg['preprocessor']["sampling_frequency"] * cfg['preprocessor']["duration"]),
                                                        in_channels=1,
                                                        out_channels=cfg["feature_size"],
                                                        kernel_size=cfg['preprocessor']["kernel_size"],
                                                        stride=cfg['preprocessor']["stride"],
                                                        padding=cfg['preprocessor']["padding"],
                                                        dilation=cfg['preprocessor']["dilation"])
                    self.feature_size = cfg["feature_size"]
                self.preprocessor_weight_decay = 0.000

            """
            Prepare sequence network
            """
            # Get Feature size
            if self.feature_size is None:
                self.feature_size = cfg["feature_size"]

            input_size = self.feature_size

            # Get activation function
            if cfg["activation"] == 'LeakyReLU':
                self.activation = torch.nn.LeakyReLU(0.2)
            elif cfg["activation"] == 'PReLU':
                self.activation = torch.nn.PReLU()
            elif cfg["activation"] == 'ReLU6':
                self.activation = torch.nn.ReLU6()
            else:
                self.activation = torch.nn.ReLU()

            # Create sequential object for the first part of the network
            segmental_layers = []
            for k in cfg["segmental"].keys():
                if k.startswith("lin"):
                    segmental_layers.append((k, torch.nn.Linear(input_size,
                                                                cfg["segmental"][k]["output"])))
                    input_size = cfg["segmental"][k]["output"]

                elif k.startswith("conv"):
                    segmental_layers.append((k, torch.nn.Conv1d(input_size,
                                                                cfg["segmental"][k]["output_channels"],
                                                                kernel_size=cfg["segmental"][k]["kernel_size"],
                                                                dilation=cfg["segmental"][k]["dilation"])))
                    input_size = cfg["segmental"][k]["output_channels"]

                elif k.startswith("activation"):
                    segmental_layers.append((k, self.activation))

                elif k.startswith('batch_norm'):
                    segmental_layers.append((k, torch.nn.BatchNorm1d(input_size)))

            self.sequence_network = torch.nn.Sequential(OrderedDict(segmental_layers))
            self.sequence_network_weight_decay = cfg["segmental"]["weight_decay"]

            """
            Pooling
            """
            self.stat_pooling = MeanStdPooling()
            tmp_input_size = input_size * 2
            if cfg["stat_pooling"]["type"] == "GRU":
                self.stat_pooling = GruPooling(input_size=cfg["stat_pooling"]["input_size"],
                                               gru_node=cfg["stat_pooling"]["gru_node"],
                                               nb_gru_layer=cfg["stat_pooling"]["nb_gru_layer"])
                tmp_input_size = cfg["stat_pooling"]["gru_node"]

            self.stat_pooling_weight_decay = cfg["stat_pooling"]["weight_decay"]

            """
            Prepare last part of the network (after pooling)
            """
            # Create sequential object for the second part of the network
            input_size = tmp_input_size
            before_embedding_layers = []
            for k in cfg["before_embedding"].keys():
                if k.startswith("lin"):
                    if cfg["before_embedding"][k]["output"] == "speaker_number":
                        before_embedding_layers.append((k, torch.nn.Linear(input_size, self.speaker_number)))
                    else:
                        before_embedding_layers.append((k, torch.nn.Linear(input_size,
                                                                           cfg["before_embedding"][k]["output"])))
                        input_size = cfg["before_embedding"][k]["output"]

                elif k.startswith("activation"):
                    before_embedding_layers.append((k, self.activation))

                elif k.startswith('batch_norm'):
                    before_embedding_layers.append((k, torch.nn.BatchNorm1d(input_size)))

                elif k.startswith('dropout'):
                    before_embedding_layers.append((k, torch.nn.Dropout(p=cfg["before_embedding"][k])))

            self.before_speaker_embedding = torch.nn.Sequential(OrderedDict(before_embedding_layers))
            self.before_speaker_embedding_weight_decay = cfg["before_embedding"]["weight_decay"]

            # if loss_criteria is "cce"
            # Create sequential object for the second part of the network
            if self.loss == "cce":
                after_embedding_layers = []
                for k in cfg["after_embedding"].keys():
                    if k.startswith("lin"):
                        if cfg["after_embedding"][k]["output"] == "speaker_number":
                            after_embedding_layers.append((k, torch.nn.Linear(input_size, self.speaker_number)))
                        else:
                            after_embedding_layers.append((k, torch.nn.Linear(input_size,
                                                                          cfg["after_embedding"][k]["output"])))
                            input_size = cfg["after_embedding"][k]["output"]

                    elif k.startswith('arc'):
                        after_embedding_layers.append((k, ArcLinear(input_size,
                                                                    self.speaker_number,
                                                                    margin=self.aam_margin,
                                                                    s=self.aam_s)))

                    elif k.startswith("activation"):
                        after_embedding_layers.append((k, self.activation))

                    elif k.startswith('batch_norm'):
                        after_embedding_layers.append((k, torch.nn.BatchNorm1d(input_size)))

                    elif k.startswith('dropout'):
                        after_embedding_layers.append((k, torch.nn.Dropout(p=cfg["after_embedding"][k])))

                self.after_speaker_embedding = torch.nn.Sequential(OrderedDict(after_embedding_layers))

            elif self.loss == "aam":
                self.norm_embedding = True
                self.after_speaker_embedding = ArcLinear(input_size,
                                                         self.speaker_number,
                                                         margin=self.aam_margin,
                                                         s=self.aam_s)

            self.after_speaker_embedding_weight_decay = cfg["after_embedding"]["weight_decay"]


    def forward(self, x, is_eval=False, target=None):
        """

        :param x:
        :param is_eval:
        :return:
        """
        if self.preprocessor is not None:
            x = self.preprocessor(x)

        x = self.sequence_network(x)

        # Mean and Standard deviation pooling
        x = self.stat_pooling(x)

        x = self.before_speaker_embedding(x)

        if self.norm_embedding:
            x_norm = x.norm(p=2,dim=1, keepdim=True) / 10. # Why  10. ?
            x = torch.div(x, x_norm)

        if is_eval:
            return x

        if self.loss == "cce":
            x = self.after_speaker_embedding(x)

        elif self.loss == "aam":
            if not is_eval:
                x = self.after_speaker_embedding(x,target=target)
            else:
                x = self.after_speaker_embedding(x, target=None)

        return x

    def context_size(self):
        context = 1
        if isinstance(self, Xtractor):
            for name, module in self.sequence_network.named_modules():
                if name.startswith("conv"):
                    context += module.dilation[0] * (module.kernel_size[0] - 1)
        else:
            for name, module in self.module.sequence_network.named_modules():
                if name.startswith("conv"):
                    context += module.dilation[0] * (module.kernel_size[0] - 1)
        return context

def xtrain(speaker_number,
           dataset_yaml,
           epochs=None,
           lr=None,
           model_yaml=None,
           model_name=None,
           loss=None,
           aam_margin=None,
           aam_s=None,
           patience=None,
           tmp_model_name=None,
           best_model_name=None,
           multi_gpu=True,
           clipping=False,
           opt=None,
           reset_parts=[],
           freeze_parts=[],
           num_thread=None):
    """

    :param speaker_number:
    :param dataset_yaml:
    :param epochs:
    :param lr:
    :param model_yaml:
    :param model_name:
    :param loss:
    :param aam_margin:
    :param aam_s:
    :param patience:
    :param tmp_model_name:
    :param best_model_name:
    :param multi_gpu:
    :param clipping:
    :param opt:
    :param reset_parts:
    :param freeze_parts:
    :param num_thread:
    :return:
    """
    # Add for tensorboard
    # Writer will output to ./runs/ directory by default
    #writer = SummaryWriter("runs/xvectors_experiments_2")
    writer = None

    if num_thread is None:
        num_thread = multiprocessing.cpu_count()

    logging.critical(f"Start process at {time.strftime('%H:%M:%S', time.localtime())}")

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # Start from scratch
    if model_name is None and model_yaml in ["xvector", "rawnet2"]:
        # Initialize a first model
        if model_yaml == "xvector":
            model = Xtractor(speaker_number, "xvector")
        elif model_yaml == "rawnet2":
            model = Xtractor(speaker_number, "rawnet2")
    else:
        with open(model_yaml, 'r') as fh:
            model_archi = yaml.load(fh, Loader=yaml.FullLoader)
            if epochs is None:
                epochs = model_archi["training"]["epochs"]
            if patience is None:
                patience = model_archi["training"]["patience"]
            if opt is None:
                opt = model_archi["training"]["opt"]
            if lr is None:
                lr = model_archi["training"]["lr"]
            if loss is None:
                loss = model_archi["training"]["loss"]
            if aam_margin is None and model_archi["training"]["loss"] == "aam":
                aam_margin = model_archi["training"]["aam_margin"]
            if aam_s is None and model_archi["training"]["loss"] == "aam":
                aam_s = model_archi["training"]["aam_s"]
            if tmp_model_name is None:
                tmp_model_name = model_archi["training"]["tmp_model_name"]
            if best_model_name is None:
                best_model_name = model_archi["training"]["best_model_name"]
            if multi_gpu is None:
                multi_gpu = model_archi["training"]["multi_gpu"]
            if clipping is None:
                clipping = model_archi["training"]["clipping"]

        if model_name is None:
            model = Xtractor(speaker_number, model_yaml)

         # If we start from an existing model
        else:
            # Load the model
            logging.critical(f"*** Load model from = {model_name}")
            checkpoint = torch.load(model_name)
            model = Xtractor(speaker_number, model_yaml)

            """
            Here we remove all layers that we don't want to reload
        
            """
            pretrained_dict = checkpoint["model_state_dict"]
            for part in reset_parts:
                pretrained_dict = {k: v for k, v in pretrained_dict.items() if not k.startswith(part)}

            new_model_dict = model.state_dict()
            new_model_dict.update(pretrained_dict)
            model.load_state_dict(new_model_dict)

        # Freeze required layers
        for name, param in model.named_parameters():
            if name.split(".")[0] in freeze_parts:
                param.requires_grad = False

    print(model)

    if torch.cuda.device_count() > 1 and multi_gpu:
        print("Let's use", torch.cuda.device_count(), "GPUs!")
        model = torch.nn.DataParallel(model)
    else:
        print("Train on a single GPU")
    model.to(device)

    """
    Set the dataloaders according to the dataset_yaml
    
    First we load the dataframe from CSV file in order to split it for training and validation purpose
    Then we provide those two 
    """
    with open(dataset_yaml, "r") as fh:
        dataset_params = yaml.load(fh, Loader=yaml.FullLoader)
        df = pandas.read_csv(dataset_params["dataset_description"])
    training_df, validation_df = train_test_split(df, test_size=dataset_params["validation_ratio"])
    torch.manual_seed(dataset_params['seed'])
    training_set = SideSet(dataset_yaml, 
                           set_type="train", 
                           dataset_df=training_df, 
                           chunk_per_segment=dataset_params['train']['chunk_per_segment'], 
                           overlap=dataset_params['train']['overlap'])
    training_loader = DataLoader(training_set,
                                 batch_size=dataset_params["batch_size"],
                                 shuffle=True,
                                 drop_last=True,
                                 pin_memory=True,
                                 num_workers=num_thread)

    validation_set = SideSet(dataset_yaml, set_type="validation", dataset_df=validation_df)
    validation_loader = DataLoader(validation_set,
                                   batch_size=dataset_params["batch_size"],
                                   drop_last=True,
                                   pin_memory=True,
                                   num_workers=num_thread)

    # Add for TensorBoard
    #dataiter = iter(training_loader)
    #data, labels = dataiter.next()
    #writer.add_graph(model, data)


    """
    Set the training options
    """
    if opt == 'adam':
        _optimizer = torch.optim.Adam
        _options = {'lr': lr}
    elif opt == 'rmsprop':
        _optimizer = torch.optim.RMSprop
        _options = {'lr': lr}
    else: # opt == 'sgd'
        _optimizer = torch.optim.SGD
        _options = {'lr': lr, 'momentum': 0.9}

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

    param_list = []
    if type(model) is Xtractor:
        if model.preprocessor is not None:
            param_list.append({'params': model.preprocessor.parameters(), 'weight_decay': model.preprocessor_weight_decay})
        param_list.append({'params': model.sequence_network.parameters(), 'weight_decay': model.sequence_network_weight_decay})
        param_list.append({'params': model.stat_pooling.parameters(), 'weight_decay': model.stat_pooling_weight_decay})
        param_list.append({'params': model.before_speaker_embedding.parameters(), 'weight_decay': model.before_speaker_embedding_weight_decay})
        param_list.append({'params': model.after_speaker_embedding.parameters(), 'weight_decay': model.after_speaker_embedding_weight_decay})

    else:
        if model.module.preprocessor is not None:
            param_list.append({'params': model.module.preprocessor.parameters(), 'weight_decay': model.module.preprocessor_weight_decay})
        param_list.append({'params': model.module.sequence_network.parameters(), 'weight_decay': model.module.sequence_network_weight_decay})
        param_list.append({'params': model.module.stat_pooling.parameters(), 'weight_decay': model.module.stat_pooling_weight_decay})
        param_list.append({'params': model.module.before_speaker_embedding.parameters(), 'weight_decay': model.module.before_speaker_embedding_weight_decay})
        param_list.append({'params': model.module.after_speaker_embedding.parameters(), 'weight_decay': model.module.after_speaker_embedding_weight_decay})


    optimizer = _optimizer(param_list, **_options)

    #optimizer = torch.optim.SGD(params,
    #                            lr=lr,
    #                            momentum=0.9,
    #                            weight_decay=0.0005)
    #print(f"Learning rate = {lr}")

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
                            dataset_params["log_interval"],
                            device=device,
                            clipping=clipping,
                            tb_writer=writer)

        # Add the cross validation here
        accuracy, val_loss = cross_validation(model, validation_loader, device=device)
        logging.critical(f"***{time.strftime('%H:%M:%S', time.localtime())} Cross validation accuracy = {accuracy} %")

        # Decrease learning rate according to the scheduler policy
        scheduler.step(val_loss)

        # remember best accuracy and save checkpoint
        is_best = accuracy > best_accuracy
        best_accuracy = max(accuracy, best_accuracy)

        if type(model) is Xtractor:
            save_checkpoint({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'accuracy': best_accuracy,
                'scheduler': scheduler,
                'speaker_number' : speaker_number,
                'model_archi': model_archi
            }, is_best, filename=tmp_model_name+".pt", best_filename=best_model_name+'.pt')
        else:
            save_checkpoint({
                'epoch': epoch,
                'model_state_dict': model.module.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'accuracy': best_accuracy,
                'scheduler': scheduler,
                'speaker_number': speaker_number,
                'model_archi': model_archi
            }, is_best, filename=tmp_model_name+".pt", best_filename=best_model_name+'.pt')

        if is_best:
            best_accuracy_epoch = epoch
            curr_patience = patience
        else:
            curr_patience -= 1
    #writer.close()

    for ii in range(torch.cuda.device_count()):
        print(torch.cuda.memory_summary(ii))

    logging.critical(f"Best accuracy {best_accuracy * 100.} obtained at epoch {best_accuracy_epoch}")

def train_epoch(model, epoch, training_loader, optimizer, log_interval, device, clipping=False, tb_writer=None):
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
    model.train()
    criterion = torch.nn.CrossEntropyLoss(reduction='mean')

    if isinstance(model, Xtractor):
        loss_criteria = model.loss
    else:
        loss_criteria = model.module.loss

    accuracy = 0.0
    running_loss = 0.0
    for batch_idx, (data, target) in enumerate(training_loader):
        target = target.squeeze()
        target = target.to(device)
        optimizer.zero_grad()

        if loss_criteria == 'aam':
            output = model(data.to(device), target=target)
        else:
            output = model(data.to(device), target=None)

        #with GuruMeditation():
        loss = criterion(output, target)
        if not torch.isnan(loss):
            loss.backward()
            if clipping:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.)
            running_loss += loss.item()
            optimizer.step()

            running_loss += loss.item()
            accuracy += (torch.argmax(output.data, 1) == target).sum()
            if batch_idx % log_interval == 0:
                batch_size = target.shape[0]
                logging.critical('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}\tAccuracy: {:.3f}'.format(
                    epoch, batch_idx + 1, training_loader.__len__(),
                    100. * batch_idx / training_loader.__len__(), loss.item(),
                    100.0 * accuracy.item() / ((batch_idx + 1) * batch_size)))
                #tb_writer.add_scalar('training loss',
                #                     running_loss / log_interval,
                #                     epoch * len(training_loader) + batch_idx)
                #tb_writer.add_scalar('training_accuracy',
                #                      100.0 * accuracy.item() / ((batch_idx + 1) * batch_size),
                #                      epoch * len(training_loader) + batch_idx)

                # ...log a Matplotlib Figure showing the model's predictions on a
                # random mini-batch
                #tb_writer.add_figure('predictions vs. actuals',
                #                     plot_classes_preds(model, data.to(device), target.to(device)),
                #                     global_step=epoch * len(training_loader) + batch_idx)

        else:
            save_checkpoint({
                             'epoch': epoch,
                             'model_state_dict': model.state_dict(),
                             'optimizer_state_dict': optimizer.state_dict(),
                             'accuracy': 0.0,
                             'scheduler': 0.0
                             }, False, filename="model_loss_NAN.pt", best_filename='toto.pt')
            with open("batch_loss_NAN.pkl", "wb") as fh:
                pickle.dump(data.cpu(), fh)
            import sys
            sys.exit()
        running_loss = 0.0
    return model


def cross_validation(model, validation_loader, device):
    """

    :param model:
    :param validation_loader:
    :param device:
    :return:
    """
    model.eval()

    if isinstance(model, Xtractor):
        loss_criteria = model.loss
    else:
        loss_criteria = model.module.loss

    accuracy = 0.0
    loss = 0.0
    criterion = torch.nn.CrossEntropyLoss()
    with torch.no_grad():
        for batch_idx, (data, target) in enumerate(validation_loader):
            batch_size = target.shape[0]
            target = target.squeeze()

            if loss_criteria == "aam":
                output = model(data.to(device), target=target)
            else:
                output = model(data.to(device), target=None)

            accuracy += (torch.argmax(output.data, 1) == target.to(device)).sum()

            loss += criterion(output, target.to(device))

    return 100. * accuracy.cpu().numpy() / ((batch_idx + 1) * batch_size), \
           loss.cpu().numpy() / ((batch_idx + 1) * batch_size)


def extract_embeddings(idmap_name,
                       model_filename,
                       data_root_name,
                       device,
                       model_yaml=None,
                       speaker_number=None,
                       file_extension="wav",
                       transform_pipeline=None,
                       frame_shift=0.01,
                       frame_duration=0.025,
                       num_thread=1):
    # Load the model
    if isinstance(model_filename, str):
        checkpoint = torch.load(model_filename)
        if speaker_number is None:
            speaker_number = checkpoint["speaker_number"]
        if model_yaml is None:
            model_archi = checkpoint["model_archi"]
        model = Xtractor(speaker_number, model_archi=model_archi)
        model.load_state_dict(checkpoint["model_state_dict"])
    else:
        model = model_filename

    if isinstance(idmap_name, IdMap):
        idmap = idmap_name
    else:
        idmap = IdMap(idmap_name)

    min_duration = (model.context_size() - 1) * frame_shift + frame_duration

    # Create dataset to load the data
    dataset = IdMapSet(idmap_name=idmap_name,
                       data_root_path=data_root_name,
                       file_extension=file_extension,
                       transform_pipeline=transform_pipeline,
                       frame_rate=int(1. / frame_shift),
                       min_duration=(model.context_size() + 2) * frame_shift * 2
                       )

    dataloader = DataLoader(dataset,
                            batch_size=1,
                            shuffle=False,
                            drop_last=False,
                            pin_memory=True,
                            num_workers=num_thread)

    with torch.no_grad():

        model.eval()
        model.to(device)

        # Get the size of embeddings to extract
        name = list(model.before_speaker_embedding.state_dict().keys())[-1].split('.')[0] + '.weight'
        emb_size = model.before_speaker_embedding.state_dict()[name].shape[0]
    
        # Create the StatServer
        embeddings = StatServer()
        embeddings.modelset = idmap.leftids
        embeddings.segset = idmap.rightids
        embeddings.start = idmap.start
        embeddings.stop = idmap.stop
        embeddings.stat0 = numpy.ones((embeddings.modelset.shape[0], 1))
        embeddings.stat1 = numpy.ones((embeddings.modelset.shape[0], emb_size))

        # Process the data
        with torch.no_grad():
            for idx, (data, mod, seg, start, stop) in tqdm.tqdm(enumerate(dataloader)):
                vec = model(data.to(device), is_eval=True)
                embeddings.stat1[idx, :] = vec.detach().cpu()

    return embeddings


def extract_sliding_embedding(idmap_name,
                              window_length,
                              sample_rate,
                              overlap,
                              speaker_number,
                              model_filename,
                              model_yaml,
                              data_root_name ,
                              device,
                              file_extension="wav",
                              transform_pipeline=None):


    # From the original IdMap, create the new one to extract x-vectors
    input_idmap = IdMap(idmap_name)

    # Create temporary lists
    nb_chunks = 0
    model_names = []
    segment_names = []
    starts = []
    stops = []
    for mod, seg, start, stop in zip(input_idmap.leftids, input_idmap.rightids, input_idmap.start, input_idmap.stop):

        # Compute the number of chunks to process
        chunk_starts = numpy.arange(start,
                                    stop - int(sample_rate * window_length),
                                    int(sample_rate * (window_length - overlap)))

        # Create a numpy array to store the current x-vectors
        model_names.append(numpy.array([mod + f"_{ii}" for ii in range(len(chunk_starts))]).astype("U"))
        segment_names.append(numpy.array([seg, ] * chunk_starts.shape[0]))
        starts.append(chunk_starts)
        stops.append(chunk_starts + sample_rate * window_length)

        nb_chunks += len(chunk_starts)

    sliding_idmap = IdMap()
    sliding_idmap.leftids = numpy.hstack(model_names)
    sliding_idmap.rightids = numpy.hstack(segment_names)
    sliding_idmap.start = numpy.hstack(starts)
    sliding_idmap.stop = numpy.hstack(stops)
    assert sliding_idmap.validate()

    embeddings = extract_embeddings(sliding_idmap,
                                 speaker_number,
                                 model_filename,
                                 model_yaml,
                                 data_root_name,
                                 device,
                                 file_extension=file_extension,
                                 transform_pipeline=transform_pipeline)

    return embeddings

