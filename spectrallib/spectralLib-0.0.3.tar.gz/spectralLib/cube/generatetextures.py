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

import os

import numpy as np
import vtk
from matplotlib import pyplot as plt


def generate_textures(datacube, sRGB):
    """Generates the textures for the faces of the 3D cube

    :param datacube: Spectral datacube as a numpy ndarray.
    :param sRGB: sRGB color image generated using spectral2rgb function.
    :Return: Return list containing textures for the cube.
    """
    # saving texture image for top of the cube | +Y
    plt.imsave("top.png", sRGB)

    plt.set_cmap("jet")

    # bottom of the cube. | -Y
    bottom = datacube[:, :, -1]
    plt.imsave("bottom.png", bottom)

    # front of the cube. | +Z
    front = np.rot90(datacube[-1, :, :])
    plt.imsave("front.png", front)

    # back of the cube. | -Z
    back = np.rot90(datacube[0, :, :])
    plt.imsave("back.png", back)

    # left of the cube. | -X
    left = datacube[:, 0, :]
    plt.imsave("left.png", left)

    # right of the cube. | +X
    right = datacube[:, -1, :]
    plt.imsave("right.png", right)

    texture_list = []

    image_list = [
        "top.png",
        "bottom.png",
        "front.png",
        "back.png",
        "left.png",
        "right.png",
    ]

    for i in range(6):
        image_reader = vtk.vtkPNGReader()
        image_reader.SetFileName(image_list[i])
        image_reader.Update()

        os.remove(image_list[i])

        texture = vtk.vtkTexture()
        texture.SetInputConnection(image_reader.GetOutputPort())
        texture.InterpolateOn()
        texture_list.append(texture)

    return texture_list
