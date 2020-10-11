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

import vtk

from spectralLib.cube.generatetextures import generate_textures


def display_spectral_cube(datacube, sRGB):
    """Display 3d spectral cube in vtk window

    :param datacube: Spectral datacube of type numpy ndarray.s
    :param sRGB: sRGB color image to be used as top face of cube. Generate
                 using spectral2rgb function.
    """
    dim1, dim2, dim3 = datacube.shape
    if dim1 > dim2:
        dim1, dim2 = dim2, dim1
    texture_list = generate_textures(datacube, sRGB)

    top = vtk.vtkPlaneSource()
    bottom = vtk.vtkPlaneSource()
    front = vtk.vtkPlaneSource()
    back = vtk.vtkPlaneSource()
    left = vtk.vtkPlaneSource()
    right = vtk.vtkPlaneSource()

    plane_list = [top, bottom, front, back, left, right]

    top.SetResolution(dim1, dim2)
    top.SetOrigin(0.0, 0.0, 0.0)
    top.SetPoint1(dim1, 0.0, 0.0)
    top.SetPoint2(0.0, 0.0, -1 * dim2)

    bottom.SetResolution(dim1, dim2)
    bottom.SetOrigin(0.0, -1 * dim3, 0.0)
    bottom.SetPoint1(dim1, -1 * dim3, 0.0)
    bottom.SetPoint2(0.0, -1 * dim3, -1 * dim2)

    front.SetResolution(dim1, dim3)
    front.SetOrigin(0.0, 0.0, 0.0)
    front.SetPoint1(dim1, 0.0, 0.0)
    front.SetPoint2(0.0, -1 * dim3, 0.0)

    back.SetResolution(dim1, dim3)
    back.SetOrigin(0.0, 0.0, -1 * dim2)
    back.SetPoint1(dim1, 0.0, -1 * dim2)
    back.SetPoint2(0.0, -1 * dim3, -1 * dim2)

    left.SetResolution(dim3, dim2)
    left.SetOrigin(0.0, 0.0, 0.0)
    left.SetPoint1(0.0, -1 * dim3, 0.0)
    left.SetPoint2(0.0, 0.0, -1 * dim2)

    right.SetResolution(dim3, dim2)
    right.SetOrigin(dim1, 0.0, 0.0)
    right.SetPoint1(dim1, -1 * dim3, 0.0)
    right.SetPoint2(dim1, 0.0, -1 * dim2)

    actor_list = []

    for i in range(len(plane_list)):
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(plane_list[i].GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.SetTexture(texture_list[i])
        actor_list.append(actor)

    renderer = vtk.vtkRenderer()
    renderer_window = vtk.vtkRenderWindow()
    renderer_window.SetSize(800, 600)
    renderer_window.SetWindowName("spectralLib spectral cube viewer")
    renderer_window.AddRenderer(renderer)
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderer_window)

    for actor in actor_list:
        renderer.AddActor(actor)

    renderer.ResetCamera()
    renderer.GetActiveCamera().Azimuth(30)
    renderer.GetActiveCamera().Elevation(30)

    renderer_window.Render()
    interactor.Start()
