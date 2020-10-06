"""Music chords.

Chords are arrays of pitches which can be added to base pitches, inverted, etc.

Example:
    >>> c = 60
    ... major = find_chord('major chord')
    ... c + major
    array([60, 64, 67])
"""
from typing import Dict, Sequence
import pkgutil

import numpy as np

from klang.constants import SEMITONES_PER_OCTAVE
from klang.util import find_item, parse_music_data_from_csv


__all__ = ['find_chord', 'invert_chord']


CHORDS_CACHE: Dict[str, np.ndarray] = {}
"""Chord name to chord mapping cache."""


def find_chord(name: str) -> np.ndarray:
    """Find chord by name in chords cache.

    Examples:
        >>> find_chord('major')
        ValueError: Ambiguous name 'major'! Did you mean:
        'major chord', 'major eleventh chord', 'major ninth chord',
        'major seventh chord', 'major seventh sharp eleventh chord',
        'major sixth chord', 'major sixth ninth chord',
        'major thirteenth chord' or 'minor major seventh chord'?

        >>> find_chord('major chord')
        array([0, 4, 7])

    Args:
        name: Chord name.

    Returns:
        Chord array.

    Raises:
        ValueError: If chord name is not found or ambiguous.
    """
    return find_item(CHORDS_CACHE, name)


def _invert_up(chord: list) -> list:
    """Invert chord up by one inversion step. Helper for invert_chord()."""
    lowest, *core = chord
    return core + [lowest + SEMITONES_PER_OCTAVE]


def _invert_down(chord: list) -> list:
    """Invert chord down by one inversion step. Helper for invert_chord()."""
    *core, highest = chord
    return [highest - SEMITONES_PER_OCTAVE] + core


def invert_chord(chord: Sequence, inversion: int) -> np.ndarray:
    """Invert chord up or down.

    Example:
        >>> invert_chord([60, 64, 67], inversion=1)
        array([64, 67, 72])

    Args:
        chord: Chord sequence to invert.
        inversion: Inversion steps.

    Returns:
        Inverted chord array.
    """
    chord = list(chord)
    for _ in range(inversion):
        chord = _invert_up(chord)

    for _ in range(-inversion):
        chord = _invert_down(chord)

    return np.array(chord)


def _load_chords() -> Dict:
    """Load chords from CSV file."""
    data = pkgutil.get_data('klang.music', 'data/chords.csv')
    chords = {
        name: np.array(data)
        for name, data
        in parse_music_data_from_csv(data).items()
    }

    return chords


CHORDS_CACHE = _load_chords()
