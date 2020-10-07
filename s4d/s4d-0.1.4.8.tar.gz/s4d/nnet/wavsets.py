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

__license__ = "LGPL"
__author__ = "Anthony Larcher"
__copyright__ = "Copyright 2015-2020 Anthony Larcher and Sylvain Meignier"
__maintainer__ = "Anthony Larcher"
__email__ = "anthony.larcher@univ-lemans.fr"
__status__ = "Production"
__docformat__ = 'reStructuredText'

import numpy
import pathlib
import random
import scipy
import sidekit
import soundfile
import torch

from ..diar import Diar
from pathlib import Path
from sidekit.nnet.xsets import PreEmphasis
from sidekit.nnet.xsets import MFCC
from sidekit.nnet.xsets import CMVN
from sidekit.nnet.xsets import FrequencyMask
from sidekit.nnet.xsets import TemporalMask
from torch.utils.data import Dataset
from torchvision import transforms
from collections import namedtuple

#Segment = namedtuple('Segment', ['show', 'start_time', 'end_time'])

def framing(sig, win_size, win_shift=1, context=(0, 0), pad='zeros'):
    """
    :param sig: input signal, can be mono or multi dimensional
    :param win_size: size of the window in term of samples
    :param win_shift: shift of the sliding window in terme of samples
    :param context: tuple of left and right context
    :param pad: can be zeros or edge
    """
    dsize = sig.dtype.itemsize
    if sig.ndim == 1:
        sig = sig[:, numpy.newaxis]
    # Manage padding
    c = (context, ) + (sig.ndim - 1) * ((0, 0), )
    _win_size = win_size + sum(context)
    shape = (int((sig.shape[0] - win_size) / win_shift) + 1, 1, _win_size, sig.shape[1])
    strides = tuple(map(lambda x: x * dsize, [win_shift * sig.shape[1], 1, sig.shape[1], 1]))
    return numpy.lib.stride_tricks.as_strided(sig,
                                           shape=shape,
                                           strides=strides).squeeze()

def load_wav_segment(wav_file_name, idx, duration, seg_shift, framerate=16000):
    """

    :param wav_file_name:
    :param idx:
    :param duration:
    :param seg_shift:
    :param framerate:
    :return:
    """
    # Load waveform
    signal = sidekit.frontend.io.read_audio(wav_file_name, framerate)[0]
    tmp = framing(signal,
                  int(framerate * duration),
                  win_shift=int(framerate * seg_shift),
                  context=(0, 0),
                  pad='zeros')
    return tmp[idx], len(signal)


def mdtm_to_label(mdtm_filename,
                  start_time,
                  stop_time,
                  sample_number,
                  speaker_dict):
    """

    :param mdtm_filename:
    :param start_time:
    :param stop_time:
    :param sample_number:
    :param speaker_dict:
    :return:
    """
    diarization = Diar.read_mdtm(mdtm_filename)
    diarization.sort(['show', 'start'])

    # When one segment starts just the frame after the previous one ends, o
    # we replace the time of the start by the time of the previous stop to avoid artificial holes
    previous_stop = 0
    for ii, seg in enumerate(diarization.segments):
        if ii == 0:
            previous_stop = seg['stop']
        else:
            if seg['start'] == diarization.segments[ii - 1]['stop'] + 1:
                diarization.segments[ii]['start'] = diarization.segments[ii - 1]['stop']

    # Create the empty labels
    label = numpy.zeros(sample_number, dtype=int)

    # Compute the time stamp of each sample
    time_stamps = numpy.zeros(sample_number, dtype=numpy.float32)
    period = (stop_time - start_time) / sample_number
    for t in range(sample_number):
        time_stamps[t] = start_time + (2 * t + 1) * period / 2

    # Find the label of the
    # first sample
    seg_idx = 0
    while diarization.segments[seg_idx]['stop'] / 100. < start_time:
        seg_idx += 1

    for ii, t in enumerate(time_stamps):
        # Si on est pas encore dans le premier segment qui overlape (on est donc dans du non-speech)
        if t <= diarization.segments[seg_idx]['start']/100.:
            # On laisse le label 0 (non-speech)
            pass
        # Si on est déjà dans le premier segment qui overlape
        elif diarization.segments[seg_idx]['start']/100. < t < diarization.segments[seg_idx]['stop']/100. :
            label[ii] = speaker_dict[diarization.segments[seg_idx]['cluster']]
        # Si on change de segment
        elif diarization.segments[seg_idx]['stop']/100. < t and len(diarization.segments) > seg_idx + 1:
            seg_idx += 1
            # On est entre deux segments:
            if t < diarization.segments[seg_idx]['start']/100.:
                pass
            elif  diarization.segments[seg_idx]['start']/100. < t < diarization.segments[seg_idx]['stop']/100.:
                label[ii] = speaker_dict[diarization.segments[seg_idx]['cluster']]

    return label


def get_segment_label(label,
                      seg_idx,
                      mode,
                      duration,
                      framerate,
                      seg_shift,
                      collar_duration,
                      filter_type="gate"):
    """

    :param label:
    :param seg_idx:
    :param mode:
    :param duration:
    :param framerate:
    :param seg_shift:
    :param collar_duration:
    :param filter_type:
    :return:
    """

    # Create labels with Diracs at every speaker change detection
    spk_change = numpy.zeros(label.shape, dtype=int)
    spk_change[:-1] = label[:-1] ^ label[1:]
    spk_change = numpy.not_equal(spk_change, numpy.zeros(label.shape, dtype=int))

    # depending of the mode, generates the labels and select the segments
    if mode == "vad":
        output_label = (label > 0.5).astype(numpy.long)

    elif mode == "spk_turn":
        # Apply convolution to replace diracs by a chosen shape (gate or triangle)
        filter_sample = collar_duration * framerate * 2 + 1
        conv_filt = numpy.ones(filter_sample)
        if filter_type == "triangle":
            conv_filt = scipy.signal.triang(filter_sample)
        output_label = numpy.convolve(conv_filt, spk_change, mode='same')

    elif mode == "overlap":
        raise NotImplementedError()

    else:
        raise ValueError("mode parameter must be 'vad', 'spk_turn' or 'overlap'")

    # Create segments with overlap
    segment_label = framing(output_label,
                  int(framerate * duration),
                  win_shift=int(framerate * seg_shift),
                  context=(0, 0),
                  pad='zeros')

    return segment_label[seg_idx]


def process_segment_label(label,
                          mode,
                          framerate,
                          collar_duration,
                          filter_type="gate"):
    """

    :param label:
    :param seg_idx:
    :param mode:
    :param duration:
    :param framerate:
    :param seg_shift:
    :param collar_duration:
    :param filter_type:
    :return:
    """
    # Create labels with Diracs at every speaker change detection
    spk_change = numpy.zeros(label.shape, dtype=int)
    spk_change[:-1] = label[:-1] ^ label[1:]
    spk_change = numpy.not_equal(spk_change, numpy.zeros(label.shape, dtype=int))

    # depending of the mode, generates the labels and select the segments
    if mode == "vad":
        output_label = (label > 0.5).astype(numpy.long)

    elif mode == "spk_turn":
        # Apply convolution to replace diracs by a chosen shape (gate or triangle)
        filter_sample = int(collar_duration * framerate * 2 + 1)

        conv_filt = numpy.ones(filter_sample)
        if filter_type == "triangle":
            conv_filt = scipy.signal.triang(filter_sample)
        output_label = numpy.convolve(conv_filt, spk_change, mode='same')

    elif mode == "overlap":
        raise NotImplementedError()

    else:
        raise ValueError("mode parameter must be 'vad', 'spk_turn' or 'overlap'")

    return output_label


def seqSplit(mdtm_dir,
             duration=2.):
    """
    
    :param mdtm_dir: 
    :param duration: 
    :return: 
    """
    segment_list = Diar()
    speaker_dict = dict()
    idx = 0
    # For each MDTM
    for mdtm_file in pathlib.Path(mdtm_dir).glob('*.mdtm'):

        # Load MDTM file
        ref = Diar.read_mdtm(mdtm_file)
        ref.sort()
        last_stop = ref.segments[-1]["stop"]

        # Get the borders of the segments (not the start of the first and not the end of the last

        # For each border time B get a segment between B - duration and B + duration
        # in which we will pick up randomly later
        for idx, seg in enumerate(ref.segments):
            if idx > 0 and seg["start"] / 100. > duration and seg["start"] + duration < last_stop:
                segment_list.append(show=seg['show'],
                                    cluster="",
                                    start=float(seg["start"]) / 100. - duration,
                                    stop=float(seg["start"]) / 100. + duration)

            elif idx < len(ref.segments) - 1 and seg["stop"] + duration < last_stop:
                segment_list.append(show=seg['show'],
                                    cluster="",
                                    start=float(seg["stop"]) / 100. - duration,
                                    stop=float(seg["stop"]) / 100. + duration)

        # Get list of unique speakers
        speakers = ref.unique('cluster')
        for spk in speakers:
            if not spk in speaker_dict:
                speaker_dict[spk] =  idx
                idx += 1

    return segment_list, speaker_dict


class SeqSet(Dataset):
    """
    Object creates a dataset for sequence to sequence training
    """
    def __init__(self,
                 dataset_yaml,
                 wav_dir,
                 mdtm_dir,
                 mode,
                 duration=2.,
                 filter_type="gate",
                 collar_duration=0.1,
                 audio_framerate=16000,
                 output_framerate=100,
                 transform_pipeline=""):
        """

        :param wav_dir:
        :param mdtm_dir:
        :param mode:
        :param duration:
        :param filter_type:
        :param collar_duration:
        :param audio_framerate:
        :param output_framerate:
        :param transform_pipeline:
        """

        self.wav_dir = wav_dir
        self.mdtm_dir = mdtm_dir
        self.mode = mode
        self.duration = duration
        self.filter_type = filter_type
        self.collar_duration = collar_duration
        self.audio_framerate = audio_framerate
        self.output_framerate = output_framerate

        self.transform_pipeline = transform_pipeline

        _transform = []
        if not self.transform_pipeline == '':
            trans = self.transform_pipeline.split(',')
            for t in trans:
                if 'PreEmphasis' in t:
                    _transform.append(PreEmphasis())
                if 'MFCC' in t:
                    _transform.append(MFCC())
                if "CMVN" in t:
                    _transform.append(CMVN())
                if "FrequencyMask" in t:
                    a = int(t.split('-')[0].split('(')[1])
                    b = int(t.split('-')[1].split(')')[0])
                    _transform.append(FrequencyMask(a, b))
                if "TemporalMask" in t:
                    a = int(t.split("(")[1].split(")")[0])
                    _transform.append(TemporalMask(a))
        self.transforms = transforms.Compose(_transform)

        segment_list, speaker_dict = seqSplit(mdtm_dir=self.mdtm_dir,
                                              duration=self.duration)
        self.segment_list = segment_list
        self.speaker_dict = speaker_dict
        self.len = len(segment_list)

    def __getitem__(self, index):
        """
        On renvoie un segment wavform brut mais il faut que les labels soient échantillonés à la bonne fréquence
        (trames)
        :param index:
        :return:
        """
        # Get segment info to load from
        seg = self.segment_list[index]

        # Randomly pick an audio chunk within the current segment
        start = random.uniform(seg["start"], seg["start"] + self.duration)

        sig, _ = soundfile.read(self.wav_dir + seg["show"] + ".wav",
                                start=int(start * self.audio_framerate),
                                stop=int((start + self.duration) * self.audio_framerate)
                                )
        sig += 0.0001 * numpy.random.randn(sig.shape[0])

        if self.transform_pipeline:
            sig, speaker_idx, _, __, _t, _s = self.transforms((sig, None,  None, None, None, None))

        tmp_label = mdtm_to_label(mdtm_filename=self.mdtm_dir + seg["show"] + ".mdtm",
                                  start_time=start,
                                  stop_time=start + self.duration,
                                  sample_number=sig.shape[1],
                                  speaker_dict=self.speaker_dict)

        label = process_segment_label(label=tmp_label,
                                      mode=self.mode,
                                      framerate=self.output_framerate,
                                      collar_duration=self.collar_duration,
                                      filter_type=self.filter_type)

        return torch.from_numpy(sig.T).type(torch.FloatTensor), torch.from_numpy(label.astype('long'))

    def __len__(self):
        return self.len
