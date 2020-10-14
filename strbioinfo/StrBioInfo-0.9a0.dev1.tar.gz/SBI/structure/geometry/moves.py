# -*- coding: utf-8 -*-
"""
.. codeauthor:: Jaume Bonet <jaume.bonet@gmail.com>

.. affiliation::
    Structural BioInformatics Lab <sbi.upf.edu>
    Baldo Oliva <baldo.oliva@upf.edu>

.. module:: structure.geometry.moves
   :platform: Unix, Windows
   :synopsis: Geometric Calculations that change the input coordinates.
"""
# Standard Libraries

# External Libraries
import numpy as np
from scipy.spatial.transform import Rotation

# This Library
from . import basics


def translate( coordinates, vector=None ):
    """Translate the coordinates according to the provided vector.

    :param coordinates: Matrix of 3D points.
    :type coordinates: :class:`~numpy.ndarray`
    :param vector: 3D vector to apply to the Frame3D.
    :param vector: Optional[:class:`~numpy.ndarray`]

    :return: :class:`~numpy.matrix`

    :raise:
        :ValueError: If vector has the wrong dimensionality.
    """
    # If nothing is provided, substitute by the empty vector
    vector = np.zeros(3, float) if vector is None else vector

    # Check proper dimensionality
    vector = np.asarray(vector)
    if len(vector.shape) != 1 and vector.shape[0] != 3:
        raise ValueError("The provided vector is not a 3D vector.")

    # We perform the operation only if it is really needed
    coordinates = np.asarray(coordinates)
    if not np.allclose(np.zeros(3, float), vector):
        coordinates += vector

    return coordinates.astype('float32')


def rotate( coordinates, matrix=None, center=None ):
    """Rotate the coordinates over a given point.

    :param coordinates: Matrix of 3D points.
    :type coordinates: :class:`~numpy.ndarray`
    :param matrix: 3D matrix (3x3) to apply to coordinates.
    :param matrix: Optional[Union[:class:`~numpy.ndarray`,
        :class:`~scipy.spatial.transform.Rotation`]]
    :param center: Point over which rotate.
        Default is the center of coordinates (``[0., 0., 0.]``).
    :param center: Optional[:class:`~numpy.ndarray`]

    :return: :class:`~numpy.matrix`

    :raise:
        :ValueError: If ``matrix`` does not have the right dimensionality.
    """
    # If nothing is provided, substitute by the non-rotating matrix
    if matrix is None:
        matrix = np.identity(3, float)
    # If matrix is not a Rotation object, we make it into one
    # (this checks proper dimensionality too)
    if not isinstance(matrix, Rotation):
        matrix = Rotation.from_dcm(matrix)

    coordinates = translate(coordinates, center if center is None else -np.asarray(center))
    coordinates = matrix.apply(coordinates)
    return translate(coordinates, center)


def rotate_euler( coordinates, x=0, y=0, z=0, center=None, degrees=False ):
    """Counter-clock rotate the coordinates over a given point.

    ..warning::
        Rotating multiple eugler angles simultaneusly is counter intuitive. Provide one angle at a time.

    :param coordinates: Matrix of 3D points.
    :type coordinates: :class:`~numpy.ndarray`
    :param float x: Degrees to rotate in the ``x`` axis.
    :param float y: Degrees to rotate in the ``y`` axis.
    :param float z: Degrees to rotate in the ``z`` axis.
    :param center: Point over which rotate.
        Default is the center of coordinates (``[0., 0., 0.]``).
    :param bool degrees: Use degrees instead of radiants.

    :raise:
        :AttributeError: If more than one angle is provided.

    :return: :class:`~numpy.matrix`
    """
    angDCT = {'x': x, 'y': y, 'z': z}
    angles = [k for k, v in angDCT.items() if v != 0]
    if len(angles) == 0:
        return coordinates
    if len(angles) > 1:
        raise AttributeError('Only one euclidean angle at a time is allowed to rotate.')
    R = Rotation.from_euler(angles[0], angDCT[angles[0]], degrees=degrees)
    return rotate(coordinates, R, center)


def yaw( coordinates, angle, degrees=False ):
    """Counter-clock rotate an object around its **perpendicular** eigenvector in its own geometric center.

    Naming of the movement follows the logic of
    `aircraft principal axes <https://www.wikiwand.com/en/Aircraft_principal_axes>`_.

    :param coordinates: Matrix of 3D points.
    :type coordinates: :class:`~numpy.ndarray`
    :param float angle: Euler angle of how much to turn.
    :param bool degrees: Use degrees instead of radiants.

    :return: :class:`~numpy.matrix`
    """
    return _principal_axes_rotation( coordinates, 'perpendicular', angle, degrees=degrees)


def pitch( coordinates, angle, degrees=False ):
    """Counter-clock rotate an object around its **side** eigenvector in its own geometric center.

    Naming of the movement follows the logic of
    `aircraft principal axes <https://www.wikiwand.com/en/Aircraft_principal_axes>`_.

    :param coordinates: Matrix of 3D points.
    :type coordinates: :class:`~numpy.ndarray`
    :param float angle: Euler angle of how much to turn.
    :param bool degrees: Use degrees instead of radiants.

    :return: :class:`~numpy.matrix`
    """
    return _principal_axes_rotation( coordinates, 'side', angle, degrees=degrees)


def roll( coordinates, angle, degrees=False ):
    """Counter-clock rotate an object around its **major** eigenvector in its own geometric center.

    Naming of the movement follows the logic of
    `aircraft principal axes <https://www.wikiwand.com/en/Aircraft_principal_axes>`_.

    :param coordinates: Matrix of 3D points.
    :type coordinates: :class:`~numpy.ndarray`
    :param float angle: Euler angle of how much to turn.
    :param bool degrees: Use degrees instead of radiants.

    :return: :class:`~numpy.matrix`
    """
    return _principal_axes_rotation( coordinates, 'major', angle, degrees=degrees)


def _principal_axes_rotation( coordinates, axis, angle, degrees=False ):
    """Counter-clock rotate an object around the selected axis in its own geometric center.

    :param coordinates: Matrix of 3D points.
    :type coordinates: :class:`~numpy.ndarray`
    :param str axis: Eigenvector over which the rotation is to be performed. Options are
        **perpendicular**, **side** and **major**.
    :param float angle: Euler angle of how much to turn.
    :param bool degrees: Use degrees instead of radiants.

    :return: :class:`~numpy.matrix`
    """
    pax = {'perpendicular': 0, 'side': 1, 'major': 2}
    return rotate(coordinates,
                  _rotation_on_vector(np.subtract(*np.flipud(basics.eigenvectors(coordinates)[pax[axis]][1:])),
                                      np.deg2rad(angle) if degrees else angle),
                  basics.geometric_center(coordinates))


def _rotation_on_vector( vector, angle ):
    """Generate the counter-clock rotation around the provided vector.

    Matrix fixing following `Paul Bourke's <http://paulbourke.net/geometry/rotate/>`_ explanations.

    :param vector: Vector around which the rotation has to take place.
    :type vector: :class:`~numpy.ndarray`
    :param float angle: Euler angle of how much to turn. In radiants.

    :return: :class:`~scipy.spatial.transform.Rotation`
    """
    n = basics.unit_vector(vector)
    q = np.square(n)

    # Matrix common factors
    c = np.cos(angle)
    t = (1 - np.cos(angle))
    s = n * np.sin(angle)

    mtrx = np.asarray([[t * q[0] + c, t * n[0] * n[1] - s[2], t * n[0] * n[2] + s[1]],
                       [t * n[0] * n[1] + s[2], t * q[1] + c, t * n[1] * n[2] - s[0]],
                       [t * n[0] * n[2] - s[1], t * n[1] * n[2] + s[0], t * q[2] + c]])
    return Rotation.from_dcm(mtrx)
