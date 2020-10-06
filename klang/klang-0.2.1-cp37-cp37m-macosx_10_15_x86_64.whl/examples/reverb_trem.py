"""Reverb demo."""
from typing import Tuple
import functools
import math

import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
from scipy.signal import lfilter

from klang.audio import AR, MonophonicSynthesizer, Oscillator, Reverb, Voice, Tremolo, square
from klang.audio import Delay
from klang.audio.filters import EchoFilter
from klang.audio.helpers import DT, INTERVAL
from klang.audio.helpers import get_time
from klang.audio.oscillators import Oscillator, Phasor, PwmOscillator
from klang.block import Block
from klang.composite import Composite
from klang.config import BUFFER_SIZE, SAMPLING_RATE
from klang.connections import Input, Relay, Output
from klang.constants import TAU, INF
from klang.klang import Dac, run_klang
from klang.math import clip
from klang.music import DOTTED_HALF_NOTE
from klang.music import SIXTEENTH_NOTE, WHOLE_NOTE, HALF_NOTE
from klang.music.note_values import QUARTER_NOTE, EIGHT_NOTE, DOTTED_EIGHT_NOTE
from klang.sequencer import Sequencer


def create_synthesizer(attack=.01, release=1.):
    """Create a monophonic synthesizer instance."""
    osc = Oscillator()
    env = AR(attack, release)
    voice = Voice(osc, env)
    return MonophonicSynthesizer(voice)


dac = (
    Sequencer([[
        #60, 62, 0, 67,
        #69, 0, 70, 60,
        #62, 67, 0, 69,
        #70, 0, 72, 0,

        #60, 60, 0, 0,
        #62, 60, 0, 0,
        #69, 67, 0, 0,
        #70, 0, 72, 0,

        #60, 67, 0, 0,
        #62, 69, 0, 0,
        #63, 72, 0, 0,
        #65, 74, 0, 0,

        60, 62, 0, 67,
        69, 0, 70, 62,
        0, 72, 63, 0,
        74, 0, 65, 0,
    ]], tempo=80)
    | create_synthesizer()
    #| Delay(DOTTED_EIGHT_NOTE, feedback=.5, drywet=.5)
    #| Reverb(decay=5., dryWet=1., echoType=EchoFilter)
    | Reverb(decay=5., dryWet=1.)
    | Tremolo(WHOLE_NOTE, smoothness=.1, dutyCycle=.25, depth=1.)
    | Delay(DOTTED_EIGHT_NOTE, feedback=.3, drywet=1.)
    #| Tremolo(depth=1.)
    | Dac(nChannels=1)
)


if __name__ == '__main__':
    run_klang(dac)
