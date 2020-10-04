from pathlib import Path

import numpy as np
np.seterr(all='raise')
import pytest
from imageio import imread

from pymartini import Martini, decode_ele

def this_dir():
    try:
        return Path(__file__).resolve().parents[0]
    except NameError:
        return Path('.').resolve()

png_fname = 'fuji'
encoding = 'mapbox'

# Generate terrain output in Python
path = this_dir() / f'data/{png_fname}.png'
png = imread(path)
terrain = decode_ele(png, encoding=encoding, backfill=False).flatten('C')

height = width = 512

self = Delatin(terrain, 512, 512)
%time self.run(1000)
self.getMaxError()
len(self.triangles)
self.coords


test = Delatin(terrain, 512, 512)
test.getMaxError()
test.run(1 * 1e3)
test.triangles
test.coords
test.triangles
len(test.triangles)

Delatin

self = Delatin(terrain, 512, 512)
%time self.run(100)
len(self.triangles)

self = Delatin(terrain, 512, 512)
%time self.run(1000)
self.coords
self.triangles
len(self.triangles)

# Lists
self = Delatin(terrain, 512, 512)
%time self.run(100)
self.coords
self.triangles
len(self.triangles)
len(self.coords) / 2

# Numpy
self = Delatin(terrain, 512, 512)
%time self.run(100)
self.coords
[:self.coordCount * 2]
self.triangles
len(self.triangles)
self.coordCount


%time self.run(1000)
self.coords

len(self.triangles)
self.coords


self._addPoint(0, 0)
self.coords[:8]
self.coordCount
self.triangles
self.coords.max()

np.uint8(255) * np.uint8(255)
np.int
