# This file is part of spectralLib.
#
# Copyright 2020, Tom George Ampiath, All rights reserved.
#
# spectralLib is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# spectralLib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with spectralLib.  If not, see <http://www.gnu.org/licenses/>.

from bisect import bisect

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import PchipInterpolator

from spectralLib.CIE.illuminant import get_illuminant
from spectralLib.CIE.observer import get_observer
from spectralLib.load.file import load_file


def spectral2rgb(datacube, wavelength, illuminant=65, year=1931, threshold=0.002):
    """Convert spectral image to sRGB color image.

    :param datacube: Spectral datacube as a numpy ndarray.
    :param wavelength: List of wavelength for each band in the spectral datacube.
    :param illuminant: Reference illuminant to be used. Values 50, 55, 65, 75
                       corresponds to d50m d55, d65 and d75 illuminants
                       respectively. (default 65)
    :param year: Year of CIE standard observer specification. (default 1931)
    :param threshold: Threshold value for contrast increase. (default 0.002)
    :return: sRGB color image.
    """
    (ydim, xdim, zdim) = datacube.shape

    observer = get_observer(year)

    observer_wavelength = observer["wavelength"]
    xbar = observer["xbar"]
    ybar = observer["ybar"]
    zbar = observer["zbar"]

    illuminant = get_illuminant(illuminant)
    illuminant_wavelength = [w for w in range(300, 781, 5)]

    # interpolate to image wavelength
    illuminant = PchipInterpolator(illuminant_wavelength, illuminant, extrapolate=True)(
        wavelength
    )
    xbar = PchipInterpolator(observer_wavelength, xbar, extrapolate=True)(wavelength)
    ybar = PchipInterpolator(observer_wavelength, ybar, extrapolate=True)(wavelength)
    zbar = PchipInterpolator(observer_wavelength, zbar, extrapolate=True)(wavelength)

    # Truncate at 780 nm wavelength
    b = bisect(wavelength, 780)
    # Reshape datacube to make each column contain spectra of one pixel and normalize it to range 0-1
    datacube = np.reshape(datacube, [-1, zdim]) / datacube.max()
    datacube = datacube[:, 0:b] / datacube.max()

    wavelength = wavelength[:b]
    illuminant = illuminant[:b]
    xbar = xbar[:b]
    ybar = ybar[:b]
    zbar = zbar[:b]

    N = 1 / np.trapz(ybar * illuminant, wavelength)

    X = N * np.trapz(datacube @ np.diag(illuminant * xbar), wavelength, axis=1)
    Y = N * np.trapz(datacube @ np.diag(illuminant * ybar), wavelength, axis=1)
    Z = N * np.trapz(datacube @ np.diag(illuminant * zbar), wavelength, axis=1)

    XYZ = np.array([X, Y, Z])

    M = np.array(
        [
            [3.2404542, -1.5371385, -0.4985314],
            [-0.9692660, 1.8760108, 0.0415560],
            [0.0556434, -0.2040259, 1.0572252],
        ]
    )

    sRGB = M @ XYZ

    # gamma correction
    gamma_map = sRGB > 0.0031308
    sRGB[gamma_map] = 1.055 * np.power(sRGB[gamma_map], (1.0 / 2.4)) - 0.055
    sRGB[np.invert(gamma_map)] = 12.92 * sRGB[np.invert(gamma_map)]

    # clipping values to range [0, 1]
    sRGB[sRGB > 1] = 1
    sRGB[sRGB < 0] = 0

    for idx in range(3):
        y = sRGB[idx, :]
        a, b = np.histogram(y, 100)
        b = b[:-1] + np.diff(b) / 2
        a = np.cumsum(a) / np.sum(a)
        th = b[0]
        i = a < threshold
        if i.any():
            th = b[i][-1]
        y = y - th
        y[y < 0] = 0

        a, b = np.histogram(y, 100)
        b = b[:-1] + np.diff(b) / 2
        a = np.cumsum(a) / np.sum(a)
        i = a > 1 - threshold
        th = b[i][0]
        y[y > th] = th
        y = y / th
        sRGB[idx, :] = y

    R = np.reshape(sRGB[0, :], [ydim, xdim])
    G = np.reshape(sRGB[1, :], [ydim, xdim])
    B = np.reshape(sRGB[2, :], [ydim, xdim])

    sRGB_image = np.transpose(np.array([R, G, B]), [1, 2, 0])

    return sRGB_image
