"""Music intervals.

Intervals can be frequency ratios or semitone step in equal temperament.

References:
  - https://en.wikipedia.org/wiki/Interval_(music)
  - http://huygens-fokker.org/docs/intervals.html
"""
from typing import Dict
from fractions import Fraction
import pkgutil

from klang.util import find_item
from klang.util import parse_music_data_from_csv


__all__ = ['find_interval']


PERFECT_UNISON = DIMINISHED_SECOND = 0
MINOR_SECOND = AUGMENTED_UNISON = 1
MAJOR_SECOND = DIMINISHED_THIRD = 2
MINOR_THIRD = AUGMENTED_SECOND = 3
MAJOR_THIRD = DIMINISHED_FOURTH = 4
PERFECT_FOURTH = AUGMENTED_THIRD = 5
DIMINISHED_FIFTH = AUGMENTED_FOURTH = 6
PERFECT_FIFTH = DIMINISHED_SIXTH = 7
MINOR_SIXTH = AUGMENTED_FIFTH = 8
MAJOR_SIXTH = DIMINISHED_SEVENTH = 9
MINOR_SEVENTH = AUGMENTED_SIXTH = 10
MAJOR_SEVENTH = DIMINISHED_OCTAVE = 11
PERFECT_OCTAVE = AUGMENTED_SEVENTH = 12


INTERVAL_CACHE: Dict[str, Fraction] = {}
"""Interval name to chord mapping."""


def find_interval(name: str) -> Fraction:
    """Find interval by name."""
    return find_item(INTERVAL_CACHE, name)


def _load_intervals() -> Dict:
    """Load intervals from CSV file."""
    data = pkgutil.get_data('klang.music', 'data/intervals.csv')
    intervals = {
        name: Fraction(ratio[0])
        for name, ratio in parse_music_data_from_csv(data).items()
    }

    return intervals


INTERVAL_CACHE = _load_intervals()
