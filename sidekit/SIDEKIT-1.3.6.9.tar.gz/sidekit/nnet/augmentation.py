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
Copyright 2014-2020 Anthony Larcher
"""

import collections
import numpy
import pandas
import random
import soundfile
import threading
import pyroomacoustics


Noise = collections.namedtuple('Noise', 'type file_id duration')


def normalize(wav):
    """

    :param wav:
    :return:
    """
    return wav / (numpy.sqrt(numpy.mean(wav ** 2)) + 1e-8)


def crop(signal, duration):
    """

    :return:
    """
    start =random.randint(0, signal.shape[0] - duration)
    chunk = signal[start: start + duration]

    return chunk


class AddNoise(object):
    """

    """

    def __init__(self, noise_db_csv, snr_min_max, noise_root_path, sample_rate=16000):
        """

        """
        self.snr_min = snr_min_max[0]
        self.snr_max = snr_min_max[1]
        self.noise_root_path = noise_root_path
        self.sample_rate = sample_rate

        df = pandas.read_csv(noise_db_csv)
        self.noises = []
        for index, row in df.iterrows():
            self.noises.append(Noise(type=row["type"], file_id=row["file_id"], duration=row["duration"]))

    def __call__(self, sample):
        """

        :param original:
        :param sample_rate:
        :return:
        """
        data = sample[0]
        if sample[4]:
            original_duration = len(data)

            # accumulate enough noise to cover duration of original waveform
            noises = []
            left = original_duration

            while left > 0:
                # select noise file at random
                file = random.choice(self.noises)
                noise_signal, fs = soundfile.read(self.noise_root_path + "/" + file.file_id + ".wav")

                # Load noise from file
                if not fs == self.sample_rate:
                    print("Problem")  # todo

                duration = noise_signal.shape[0]

                # if noise file is longer than what is needed, crop it
                if duration > left:
                    noise = crop(noise_signal, left)
                    left = 0

                # otherwise, take the whole file
                else:
                    noise = noise_signal
                    left -= duration
                # Todo Downsample if needed
                # if sample_rate > fs:
                #

                noise = normalize(noise)
                noises.append(noise.squeeze())

            # concatenate
            noise = numpy.hstack(noises)

            # select SNR at random
            snr = (self.snr_max - self.snr_min) * numpy.random.random_sample() + self.snr_min
            alpha = numpy.exp(-numpy.log(10) * snr / 20)

            data = normalize(data) + alpha * noise

        return data.squeeze(), sample[1], sample[2], sample[3], sample[4], sample[5]

class AddNoiseFromSilence(object):
    """

    """
    def __init__(self, noise_db_csv, snr_min_max, noise_root_path, sample_rate=16000):
        """

        """
        self.snr_min = snr_min_max[0]
        self.snr_max = snr_min_max[1]
        self.noise_root_path = noise_root_path
        self.sample_rate = sample_rate

        df = pandas.read_csv(noise_db_csv)
        self.noises = []
        for index, row in df.iterrows():
            self.noises.append(Noise(type=row["type"], file_id=row["file_id"], duration=row["duration"]))

    def __call__(self, sample):
        """

        :param original:
        :param sample_rate:
        :return:
        """
        data = sample[0]
        if sample[4]:
            original_duration = len(data)

            # accumulate enough noise to cover duration of original waveform
            noises = []
            left = original_duration

            while left > 0:
                # select noise file at random
                file = random.choice(self.noises)
                noise_signal, fs = soundfile.read(self.noise_root_path + "/" + file.file_id + ".wav")

                # Load noise from file
                if not fs == self.sample_rate:
                    print("Problem")  # todo

                duration = noise_signal.shape[0]

                # if noise file is longer than what is needed, crop it
                if duration > left:
                    noise = crop(noise_signal, left)
                    left = 0

                # otherwise, take the whole file
                else:
                    noise = noise_signal
                    left -= duration
                # Todo Downsample if needed
                # if sample_rate > fs:
                #

                noise = normalize(noise)
                noises.append(noise.squeeze())

            # concatenate
            noise = numpy.hstack(noises)

            # select SNR at random
            snr = (self.snr_max - self.snr_min) * numpy.random.random_sample() + self.snr_min
            alpha = numpy.exp(-numpy.log(10) * snr / 20)

            data = normalize(data) + alpha * noise

        return data.squeeze(), sample[1], sample[2], sample[3], sample[4], sample[5]


class AddReverb(object):
    """Simulate indoor reverberation

    Parameters
    ----------
    depth : (float, float), optional
        Minimum and maximum values for room depth (in meters).
        Defaults to (2.0, 10.0).
    width : (float, float), optional
        Minimum and maximum values for room width (in meters).
        Defaults to (1.0, 10.0).
    height : (float, float), optional
        Minimum and maximum values for room heigth (in meters).
        Defaults to (2.0, 5.0).
    absorption : (float, float), optional
        Minimum and maximum values of walls absorption coefficient.
        Defaults to (0.2, 0.9).
    noise : str or list of str, optional
        `pyannote.database` collection(s) used for adding noise.
        Defaults to "MUSAN.Collection.BackgroundNoise"
    snr : (float, float), optional
        Minimum and maximum values of signal-to-noise ratio.
        Defaults to (5.0, 15.0)

    """

    def __init__(
        self,
        depth=(2.0, 10.0),
        width=(1.0, 10.0),
        height=(2.0, 5.0),
        absorption=(0.2, 0.9),
        noise=None,
        snr=(5.0, 15.0)
    ):

        super().__init__()
        self.depth = depth
        self.width = width
        self.height = height
        self.absorption = absorption
        self.max_order_ = 17

        self.noise = noise
        self.snr = snr
        self.noise_ = noise

        self.n_rooms_ = 128
        self.new_rooms_prob_ = 0.001
        self.main_lock_ = threading.Lock()
        self.rooms_ = collections.deque(maxlen=self.n_rooms_)
        self.room_lock_ = [threading.Lock() for _ in range(self.n_rooms_)]

    @staticmethod
    def random(m, M):
        """

        :param m:
        :param M:
        :return:
        """
        return (M - m) * numpy.random.random_sample() + m

    def new_room(self, sample_rate: int):
        """

        :param sample_rate:
        :return:
        """
        # generate a room at random
        depth = self.random(*self.depth)
        width = self.random(*self.width)
        height = self.random(*self.height)
        absorption = self.random(*self.absorption)
        room = pyroomacoustics.ShoeBox(
            [depth, width, height],
            fs=sample_rate,
            absorption=absorption,
            max_order=self.max_order_,
        )

        # play the original audio chunk at a random location
        original = [
            self.random(0, depth),
            self.random(0, width),
            self.random(0, height),
        ]
        room.add_source(original)

        # play the noise audio chunk at a random location
        noise = [self.random(0, depth), self.random(0, width), self.random(0, height)]
        room.add_source(noise)

        # place the microphone at a random location
        microphone = [
            self.random(0, depth),
            self.random(0, width),
            self.random(0, height),
        ]
        room.add_microphone_array(
            pyroomacoustics.MicrophoneArray(numpy.c_[microphone, microphone], sample_rate)
        )

        room.compute_rir()

        return room

    def __call__(self, sample):

        data = sample[0]
        if sample[5]:

            with self.main_lock_:

                # initialize rooms (with 2 sources and 1 microphone)
                while len(self.rooms_) < self.n_rooms_:
                    room = self.new_room(self.sample_rate)
                    self.rooms_.append(room)

                # create new room with probability new_rooms_prob_
                if numpy.random.rand() > 1.0 - self.new_rooms_prob_:
                    room = self.new_room(self.sample_rate)
                    self.rooms_.append(room)

                # choose one room at random
                index = numpy.random.choice(self.n_rooms_)

            # lock chosen room to ensure room.sources are not updated concurrently
            with self.room_lock_[index]:

                room = self.rooms_[index]

                # play normalized original audio chunk at source #1
                n_samples = len(data)
                data = normalize(original).squeeze()
                room.sources[0].add_signal(data)

                # generate noise with random SNR
                noise = self.noise_(n_samples, self.sample_rate).squeeze()
                snr = self.random(*self.snr)
                alpha = numpy.exp(-numpy.log(10) * snr / 20)
                noise *= alpha

                # play noise at source #2
                room.sources[1].add_signal(noise)

                # simulate room and return microphone signal
                room.simulate()
                data = room.mic_array.signals[0, :n_samples, numpy.newaxis]

        return data, sample[1], sample[2], sample[3] , sample[4], sample[5]

