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

from matplotlib import pyplot as plt

from spectralLib.CIE.spectral2rgb import spectral2rgb


def display_color_image(
    datacube, wavelength, illuminant=65, year=1931, threshold=0.002
):
    """Display color image from spectral image.

    :param datacube: Spectral datacube as a numpy ndarray.
    :param wavelength: List of wavelength for each band in the spectral datacube.
    :param illuminant: Reference illuminant to be used. Values 50, 55, 65, 75
                       corresponds to d50m d55, d65 and d75 illuminants
                       respectively. (default 65)
    :param year: Year of CIE standard observer specification. (default 1931)
    :param threshold: Threshold value for contrast increase. (default 0.002)
    :return: None.
    """
    color_image = spectral2rgb(datacube, wavelength, illuminant, year, threshold)

    plt.imshow(color_image)
    plt.show()
