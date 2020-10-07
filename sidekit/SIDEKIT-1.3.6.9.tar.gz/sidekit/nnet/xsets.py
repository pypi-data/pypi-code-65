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

The authors would like to thank the BUT Speech@FIT group (http://speech.fit.vutbr.cz) and Lukas BURGET
for sharing the source code that strongly inspired this module. Thank you for your valuable contribution.
"""

import h5py
import numpy
import pandas
import pickle
import random
import torch
import tqdm
import soundfile
import yaml

from .augmentation import AddNoise
from .augmentation import AddReverb
from ..bosaris.idmap import IdMap
from ..frontend.vad import pre_emphasis
from ..frontend.features import trfbank
from ..frontend.features import framing
from torch.utils.data import Dataset
from ..frontend.io import read_dataset_percentile
from ..features_server import FeaturesServer
from scipy.fftpack.realtransforms import dct
from torchvision import transforms

__license__ = "LGPL"
__author__ = "Anthony Larcher"
__copyright__ = "Copyright 2015-2020 Anthony Larcher"
__maintainer__ = "Anthony Larcher"
__email__ = "anthony.larcher@univ-lemans.fr"
__status__ = "Production"
__docformat__ = 'reStructuredText'


wav_type = "float32"  # can be int16, float64, int32 or float32


def read_batch(batch_file):
    """
    :param batch_file:
    :return:
    """
    with h5py.File(batch_file, 'r') as h5f:
        data = read_dataset_percentile(h5f, 'data')
        label = h5f['label'][()]

        # Normalize and reshape
        data = data.reshape((len(label), data.shape[0] // len(label), data.shape[1])).transpose(0, 2, 1)
        for idx in range(data.shape[0]):
            m = data[idx].mean(axis=0)
            s = data[idx].std(axis=0)
            data[idx] = (data[idx] - m) / s
        return data, label


class XvectorDataset(Dataset):
    """
    Object that takes a list of files from a file and initialize a Dataset
    """
    def __init__(self, batch_list, batch_path):
        with open(batch_list, 'r') as fh:
            self.batch_files = [batch_path + '/' + l.rstrip() for l in fh]
            self.len = len(self.batch_files)

    def __getitem__(self, index):
        data, label = read_batch(self.batch_files[index])
        return torch.from_numpy(data).type(torch.FloatTensor), torch.from_numpy(label.astype('long'))

    def __len__(self):
        return self.len


class XvectorMultiDataset(Dataset):
    """
    Object that takes a list of files as a Python List and initialize a DataSet
    """
    def __init__(self, batch_list, batch_path):
        self.batch_files = [batch_path + '/' + l for l in batch_list]
        self.len = len(self.batch_files)

    def __getitem__(self, index):
        data, label = read_batch(self.batch_files[index])
        return torch.from_numpy(data).type(torch.FloatTensor), torch.from_numpy(label.astype('long'))

    def __len__(self):
        return self.len


class StatDataset(Dataset):
    """
    Object that initialize a Dataset from an sidekit.IdMap
    """
    def __init__(self, idmap, fs_param):
        self.idmap = idmap
        self.fs = FeaturesServer(**fs_param)
        self.len = self.idmap.leftids.shape[0]

    def __getitem__(self, index):
        data, _ = self.fs.load(self.idmap.rightids[index], start=self.idmap.start[index], stop=self.idmap.stop[index])
        data = (data - data.mean(0)) / data.std(0)
        data = data.reshape((1, data.shape[0], data.shape[1])).transpose(0, 2, 1).astype(numpy.float32)
        return self.idmap.leftids[index], self.idmap.rightids[index], torch.from_numpy(data).type(torch.FloatTensor)

    def __len__(self):
        return self.len

class VoxDataset(Dataset):
    """

    """
    def __init__(self, segment_df, speaker_dict, duration=500, transform = None, spec_aug_ratio=0.5, temp_aug_ratio=0.5):
        """

        :param segment_df:
        :param speaker_dict:
        :param duration:
        :param transform:
        :param spec_aug_ratio:
        :param temp_aug_ratio:
        """
        self.segment_list = segment_df

        self.speaker_dict = speaker_dict

        self.len = len(self.segment_list)
        self.duration = duration
        self.transform = transform
        tmp = numpy.zeros(self.len, dtype=bool)
        tmp[:int(self.len * spec_aug_ratio)] = 1
        numpy.random.shuffle(tmp)

        tmp2 = numpy.zeros(self.len, dtype=bool)
        tmp2[:int(self.len * temp_aug_ratio)] = 1
        numpy.random.shuffle(tmp2)

        self.spec_aug = tmp
        self.temp_aug = tmp2

    def __getitem__(self, index):
        """

        :return:
        """
        fh = h5py.File(self.segment_list.loc[index].hdf5_file, 'r')
        feature_size = fh[self.segment_list.session_id[index]].shape[1]

        start = int(self.segment_list.start[index])
        data = read_dataset_percentile(fh, self.segment_list.session_id[index]).T

        if not self.duration is None:
            data = data[:, start:start + self.duration]
            label = self.speaker_dict[self.segment_list.speaker_id[index]]

        else:
            label = self.segment_list.speaker_id[index]
        fh.close()

        spec_aug = False
        temp_aug = False
        if self.transform:
            data, label, spec_aug, temp_aug = self.transform((data, label, self.spec_aug[index], self.temp_aug[index]))

        if self.duration is not None:
            label = torch.from_numpy(numpy.array([label, ]).astype('long'))

        return torch.from_numpy(data).type(torch.FloatTensor), label, spec_aug, temp_aug

    def __len__(self):
        """

        :param self:
        :return:
        """
        return self.len


class PreEmphasis(object):
    """
    Perform pre-emphasis filtering on audio segment
    """
    def __init__(self, pre_emp_value=0.97):
        self.pre_emp_value = pre_emp_value

    def __call__(self, sample):
        data = numpy.asarray(sample[0][1:] - 0.97 * sample[0][:-1], dtype=numpy.float32)
        return data, sample[1], sample[2], sample[3], sample[4], sample[5]


class CMVN(object):
    """Crop randomly the image in a sample.

    Args:
        output_size (tuple or int): Desired output size. If int, square crop
            is made.
    """
    def __init__(self):
        pass

    def __call__(self, sample):
        m = sample[0].mean(axis=0)
        s = sample[0].std(axis=0)
        data = (sample[0] - m) / s
        return data, sample[1], sample[2], sample[3], sample[4], sample[5]


class FrequencyMask(object):
    """Crop randomly the image in a sample.

    Args:
        output_size (tuple or int): Desired output size. If int, square crop
            is made.
    """
    def __init__(self, max_size, feature_size):
        self.max_size = max_size
        self.feature_size = feature_size

    def __call__(self, sample):
        data = sample[0]
        if sample[2]:
            size = numpy.random.randint(1, self.max_size)
            f0 = numpy.random.randint(0, self.feature_size - self.max_size)
            data[f0:f0+size, :] = 10.
        return data, sample[1], sample[2], sample[3], sample[4], sample[5]


class TemporalMask(object):
    """Crop randomly the image in a sample.

    Args:
        output_size (tuple or int): Desired output size. If int, square crop
            is made.
    """
    def __init__(self, max_size):
        self.max_size = max_size

    def __call__(self, sample):
        data = sample[0]
        if sample[3]:
            size = numpy.random.randint(1, self.max_size)
            t0 = numpy.random.randint(0, sample[0].shape[1] - self.max_size)
            data[:, t0:t0+size] = 10.
        return data, sample[1], sample[2], sample[3], sample[4], sample[5]


class MFCC(object):
    """Compute MFCC on the segment.

    Args:
        output_size (tuple or int): Desired output size. If int, square crop
            is made.
    """
    def __init__(self, lowfreq=133.333, maxfreq=6855.4976,
                 nlinfilt=0, nlogfilt=40,
                 win_time=0.025,
                 fs=16000,
                 nceps=30,
                 shift=0.01,
                 prefac=0.97
                 ):
        """

        :param lowfreq:
        :param maxfreq:
        :param nlinfilt:
        :param nlogfilt:
        :param win_time:
        :param fs:
        :param nceps:
        :param shift:
        :param prefac:
        """
        self.fs = fs
        self.nceps = nceps
        self.window_length = int(round(win_time * fs))
        self.overlap = self.window_length - int(shift * fs)
        self.prefac = prefac
        self.n_fft = 2 ** int(numpy.ceil(numpy.log2(self.window_length)))
        self.fbank = (trfbank(self.fs, self.n_fft, lowfreq, maxfreq, nlinfilt, nlogfilt)[0]).T

    def __call__(self, sample):
        """

        :param sample:
        :return:
        """
        sig = sample[0][:, numpy.newaxis] # ajout
        framed = framing(sample[0], self.window_length, win_shift=self.window_length - self.overlap).copy()
        framed = framing(sample[0], self.window_length, win_shift=self.window_length - self.overlap).copy()
        # Pre-emphasis filtering is applied after framing to be consistent with stream processing
        framed = pre_emphasis(framed, self.prefac)
        # Windowing has been changed to hanning which is supposed to have less noisy sidelobes
        # ham = numpy.hamming(window_length)
        window = numpy.hanning(self.window_length)
        log_energy = numpy.log((framed ** 2).sum(axis=1))
        mag = numpy.fft.rfft(framed * window, self.n_fft, axis=-1)
        spec = mag.real ** 2 + mag.imag ** 2
        # Filter the spectrum through the triangle filter-bank
        mspec = numpy.log(numpy.dot(spec, self.fbank))  # A tester avec log10 et log
        # Use the DCT to 'compress' the coefficients (spectrum -> cepstrum domain)
        # The C0 term is removed as it is the constant term
        mfcc = dct(mspec, type=2, norm='ortho', axis=-1)[:, 1:self.nceps + 1]
        return mfcc.T, sample[1], sample[2], sample[3], sample[4], sample[5]



class SideSet(Dataset):

    def __init__(self,
                 data_set_yaml,
                 set_type="train",
                 chunk_per_segment=1,
                 overlap=0.,
                 dataset_df=None,
                 min_duration=0.165
                 ):
        """

        :param dataset_yaml: name of the YAML file describing the dataset
        :param set_type: string, can be "train" or "validation"
        :param chunk_per_segment: number of chunks to select for each segment
        default is 1 and -1 means select all possible chunks
        """
        with open(data_set_yaml, "r") as fh:
            dataset = yaml.load(fh, Loader=yaml.FullLoader)

        self.data_path = dataset["data_root_directory"]
        self.sample_rate = int(dataset["sample_rate"])
        self.data_file_extension = dataset["data_file_extension"]
        self.transformation = ''
        self.min_duration = min_duration


        if set_type == "train":
            self.duration = dataset["train"]["duration"]
            self.transformation  = dataset["train"]["transformation"]
        else:
            self.duration = dataset["eval"]["duration"]
            self.transformation  = dataset["eval"]["transformation"]

        self.sample_number = int(self.duration * self.sample_rate)

        # Load the dataset description as pandas.dataframe
        if dataset_df is None:
            df = pandas.read_csv(dataset["dataset_description"])
        else:
            assert isinstance(dataset_df, pandas.DataFrame)
            df = dataset_df

        # From each segment which duration is longer than the chosen one
        # select the requested segments
        if set_type == "train":
            tmp_sessions = df.loc[df['duration'] > self.duration]
        else:
            if not "duration" == '':
                tmp_sessions = df.loc[df['duration'] > self.duration]
            else:
                self.sessions = df

        # Create lists for each column of the dataframe
        df_dict = dict(zip(df.columns, [[], [], [], [], [], [], []]))

        # For each segment, get all possible segments with the current overlap
        for idx in tqdm.trange(len(tmp_sessions)):
            # Compute possible starts 
            possible_starts = numpy.arange(0,
                                           int(self.sample_rate * (df.iloc[idx].duration - self.duration)),
                                           self.sample_number - int(self.sample_rate * overlap)
                                           )
            possible_starts += int(self.sample_rate * df.iloc[idx].start)

            # Select max(seg_nb, possible_segments) segments
            if chunk_per_segment == -1:
                starts = possible_starts
                chunk_nb = len(possible_starts)
            else:
                chunk_nb = min(len(possible_starts), chunk_per_segment)
                starts = numpy.random.permutation(possible_starts)[:chunk_nb] / self.sample_rate

            # Once we know how many segments are selected, create the other fields to fill the DataFrame
            for ii in range(chunk_nb):
                df_dict["database"].append(df.iloc[idx].database)
                df_dict["speaker_id"].append(df.iloc[idx].speaker_id)
                df_dict["file_id"].append(df.iloc[idx].file_id)
                df_dict["start"].append(starts[ii])
                df_dict["duration"].append(self.duration)
                df_dict["speaker_idx"].append(df.iloc[idx].speaker_idx)
                df_dict["gender"].append(df.iloc[idx].gender)

        self.sessions = pandas.DataFrame.from_dict(df_dict)
        self.len = len(self.sessions)

        _transform = []
        if (self.transformation["pipeline"] != '') and (self.transformation["pipeline"] is not None):
            trans = self.transformation["pipeline"].split(',')

            self.add_noise = numpy.zeros(self.len, dtype=bool)
            self.add_reverb = numpy.zeros(self.len, dtype=bool)
            self.spec_aug = numpy.zeros(self.len, dtype=bool)
            self.temp_aug = numpy.zeros(self.len, dtype=bool)

            for t in trans:

                if 'PreEmphasis' in t:
                    _transform.append(PreEmphasis())

                if 'add_noise' in t:
                    self.add_noise[:int(self.len * self.transformation["noise_file_ratio"])] = 1
                    numpy.random.shuffle(self.add_noise)
                    _transform.append(AddNoise(noise_db_csv=self.transformation["noise_db_csv"],
                                               snr_min_max=self.transformation["noise_snr"],
                                               noise_root_path=self.transformation["noise_root_db"]))

                if 'add_reverb' in t:
                    self.add_reverb[:int(self.len * self.transformation["reverb_file_ratio"])] = 1
                    numpy.random.shuffle(self.add_reverb)

                    _transform.append(AddReverb(depth=self.transformation["reverb_depth"],
                                                width=self.transformation["reverb_width"],
                                                height=self.transformation["reverb_height"],
                                                absorption=self.transformation["reverb_absorption"],
                                                noise=None,
                                                snr=self.transformation["reverb_snr"]))
                if 'MFCC' in t:
                    _transform.append(MFCC())

                if "CMVN" in t:
                    _transform.append(CMVN())

                if "FrequencyMask" in t:
                    # Setup temporal and spectral augmentation if any
                    self.spec_aug[:int(self.len * self.transformation["spec_aug"])] = 1
                    numpy.random.shuffle(self.spec_aug)

                    a = int(t.split('-')[0].split('(')[1])
                    b = int(t.split('-')[1].split(')')[0])
                    _transform.append(FrequencyMask(a, b))

                if "TemporalMask" in t:
                    self.temp_aug[:int(self.len * self.transformation["temp_aug"])] = 1
                    numpy.random.shuffle(self.temp_aug)

                    a = int(t.split("(")[1].split(")")[0])
                    _transform.append(TemporalMask(a))

        self.transforms = transforms.Compose(_transform)

    def __getitem__(self, index):
        """

        :return:
        """
        # Check the size of the file
        nfo = soundfile.info(f"{self.data_path}/{self.sessions.iloc[index]['file_id']}{self.data_file_extension}")
        start_frame = int(self.sessions.iloc[index]['start'] * self.sample_rate)
        if start_frame + self.sample_number >= nfo.frames:
            start_frame = numpy.min(nfo.frames - self.sample_number - 1)
        stop_frame = start_frame + self.sample_number

        sig, _ = soundfile.read(f"{self.data_path}/{self.sessions.iloc[index]['file_id']}{self.data_file_extension}",
                                start=start_frame,
                                stop=stop_frame,
                                 dtype=wav_type
                               )
        sig = sig.astype(numpy.float32)
        sig += 0.0001 * numpy.random.randn(sig.shape[0])


        speaker_idx = self.sessions.iloc[index]["speaker_idx"]

        if self.transformation["pipeline"]:
            sig, speaker_idx, _, __, _t, _s = self.transforms((sig,
                                                       speaker_idx,
                                                       self.spec_aug[index],
                                                       self.temp_aug[index],
                                                       self.add_noise[index],
                                                       self.add_reverb[index]
                                                       ))

        return torch.from_numpy(sig).type(torch.FloatTensor), speaker_idx

    def __len__(self):
        """

        :param self:
        :return:
        """
        return self.len

def createSideSets(data_set_yaml,
                   chunk_per_segment=1,
                   overlap=0.,
                   validation_ratio=None,
                   training_df=None,
                   validation_df=None):
    """
    Function that creates two SideSets for training and validation

    :param data_set_yaml:
    :param set_type:
    :param chunk_per_segment:
    :param overlap:
    :param dataset_df:
    :return:
    """


    # TODO SPLIT THE COROPORA OR USE THE TWO PROVIDED DATAFRAMES

    train_set  = SideSet(data_set_yaml,
                        "train",
                        chunk_per_segment,
                        overlap,
                        training_df)

    validation_set  = SideSet(data_set_yaml,
                             "validation",
                             chunk_per_segment,
                             overlap,
                             training_df)


class IdMapSet(Dataset):
    """
    DataSet that provide data according to a sidekit.IdMap object
    """

    def __init__(self,
                 idmap_name,
                 data_root_path,
                 file_extension,
                 transform_pipeline=None,
                 frame_rate=100,
                 min_duration=0.165
                 ):
        """

        :param data_root_name:
        :param idmap_name:
        """
        if isinstance(idmap_name, IdMap):
            self.idmap = idmap_name
        else:
            self.idmap = IdMap(idmap_name)

        self.data_root_path = data_root_path
        self.file_extension = file_extension
        self.len = self.idmap.leftids.shape[0]
        self.transform_pipeline = transform_pipeline
        self.min_duration = min_duration
        self.sample_rate = frame_rate

        _transform = []
        if transform_pipeline is not None:
            trans = transform_pipeline.split(",")
            for t in trans:
                if 'PreEmphasis' in t:
                    _transform.append(PreEmphasis())
                if 'MFCC' in t:
                    _transform.append(MFCC())
                if "CMVN" in t:
                    _transform.append(CMVN())
        self.transforms = transforms.Compose(_transform)

    def __getitem__(self, index):
        """

        :param index:
        :return:
        """
        if self.idmap.start[index] is None:
            start = 0.0

        if self.idmap.start[index] is None and self.idmap.stop[index] is None:
            sig, sample_rate = soundfile.read(f"{self.data_root_path}/{self.idmap.rightids[index]}.{self.file_extension}", dtype=wav_type)
            sig = sig.astype(numpy.float32)
            start = 0
            stop = len(sig)
        else:
            nfo = soundfile.info(f"{self.data_root_path}/{self.idmap.rightids[index]}.{self.file_extension}")
            start = int(self.idmap.start[index])
            stop = int(self.idmap.stop[index])
            # add this in case the segment is too short
            if stop - start <= self.min_duration * nfo.samplerate:
                middle = start + (stop - start) // 2
                start = max(0, int(middle - (self.min_duration * nfo.samplerate / 2)))

                stop = int(start + self.min_duration * nfo.samplerate)
            sig, _ = soundfile.read(f"{self.data_root_path}/{self.idmap.rightids[index]}.{self.file_extension}",
                                    start=start,
                                    stop=stop,
                                    dtype=wav_type)
            sig = sig.astype(numpy.float32)
        sig += 0.0001 * numpy.random.randn(sig.shape[0])

        if self.transform_pipeline is not None:
            sig, _, ___, _____, _t, _s = self.transforms((sig, 0,  0, 0, 0, 0))

        return torch.from_numpy(sig).type(torch.FloatTensor), \
               self.idmap.leftids[index], \
               self.idmap.rightids[index], \
               start, stop
               #self.idmap.start[index], self.idmap.stop[index]


    def __len__(self):
        """

        :param self:
        :return:
        """
        return self.len
