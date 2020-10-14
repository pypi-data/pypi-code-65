from dataclasses import dataclass
from typing import Tuple

from palett import Preset
from palett.presets import AZURE, MOSS


@dataclass
class DecoPreset:
    presets: Tuple[Preset, Preset] or Preset = (AZURE, MOSS)
    depth: int = 8
    vert: int = 0
    unit: int = 32
    width: int = 80
