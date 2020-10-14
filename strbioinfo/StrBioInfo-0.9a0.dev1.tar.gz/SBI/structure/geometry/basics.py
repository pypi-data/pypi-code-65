# -*- coding: utf-8 -*-
"""
.. codeauthor:: Jaume Bonet <jaume.bonet@gmail.com>

.. affiliation::
    Structural BioInformatics Lab <sbi.upf.edu>
    Baldo Oliva <baldo.oliva@upf.edu>

.. module:: structure.geometry.basics
   :platform: Unix, Windows
   :synopsis: Geometric Calculations that do not change the input coordinates.
"""
# Standard Libraries
from typing import Optional, Union, List

# External Libraries
import numpy as np
import numpy.linalg as nl
import scipy.spatial as sp

# This Library


def geometric_center( coordinates ):
    """Get the geometric center of the provided coordinates.

    :param coordinates: Matrix of 3D points.
    :type coordinates: :class:`~numpy.ndarray`

    :return: :class:`~numpy.ndarray`
    """
    return np.asarray(coordinates).mean(axis=0).astype('float32')


def eigenvectors( coordinates:  Union[List, np.ndarray],
                  module: Optional[float] = 2.0 ) -> np.ndarray:
    """Return the three eigenvectors defining the provided coordinates.

    :param coordinates: Matrix of 3D points.
    :param module: Module for the vectors.

    :return: 3 vectors, ordered as *perpendicular*, *side* and *major* eigenvectors. Each
        vector contains 3 points: starting, center and end points to match the expected module length.
    """
    coordinates = np.asarray(coordinates)
    center = geometric_center(coordinates)

    A  = np.asarray(np.zeros((3, 3)))
    P  = coordinates - center
    for p in P:
        r = np.asarray(p)
        A += r.transpose() * r
    val, EigVc = nl.eigh(A)
    vectors = []
    for axis in range(3):
        t = np.asarray(EigVc[:, axis]).reshape(3)
        vectors.append([np.around(np.asarray(center + (module / 2.0) * t, dtype=np.float32), decimals=3),
                        np.around(center, decimals=3),
                        np.around(np.asarray(center - (module / 2.0) * t, dtype=np.float32), decimals=3)])

    # Correct direction Major Axis
    if distance(vectors[2][0], coordinates[-1]) < distance(vectors[2][0], coordinates[0]):
        vectors[2] = np.flip(vectors[2], axis=0)

    return np.asarray(vectors)


def distance( vector1: Union[List, np.ndarray],
              vector2: Optional[Union[List, np.ndarray]] = None,
              metric: Optional[str] = 'euclidean',
              **kwargs ) -> Union[np.float, np.ndarray]:
    """Compute distance between *each pair* of the two collections of inputs.

    This is a wrapper around :meth:`.scipy.spatial.distance.cdist` that allows the
    second collection to be 0.

    :param vector1: First collection of coordinates.
    :param vector2: Second collection of coordinates.
    :param metric: Distance metric to apply.

    :return: A single value with the distance if two single points are provided, or a matrix
        of size ``len(point1)xlen(point2)`` if more than one point is provided by input.
    """
    points = [np.asarray(vector1), np.zeros(3, float) if vector2 is None else np.asarray(vector2)]
    for i, p in enumerate(points):
        points[i] = np.reshape(p, (1, 3)) if len(p.shape) == 1 else p

    value = sp.distance.cdist(*points, metric=metric, **kwargs)
    return value[0][0] if value.shape == (1, 1) else value


def unit_vector( vector ):
    """Generate the unit vector of the vector.

    :param vector: Vector to make unitary.
    :type vector: Union[:func:`list`, :class:`~numpy.ndarray`]

    :return: :class:`~numpy.ndarray`
    """
    return np.asarray(np.asarray(vector) / nl.norm(vector))


def vector_angle( vector1, vector2 ):
    """Calculate the angle in radians between two vectors.

    :param vector1: First 3D vector.
    :type vector1: Union[:func:`list`, :class:`~numpy.ndarray`]
    :param vector2: Second 3D vector.
    :type vector2: Union[:func:`list`, :class:`~numpy.ndarray`]

    :return: :class:`float`

    .. seealso::
        :func:`.vector_angle_xyz`
    """
    v1_u = unit_vector(vector1)
    v2_u = unit_vector(vector2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def angle( point1: Union[List, np.ndarray],
           point2: Union[List, np.ndarray],
           point3: Union[List, np.ndarray] ) -> np.float:
    """Calculate the angle **in radiants** between 3 points.

    :param point1: First 3D point.
    :param point2: Second 3D point.
    :param point3: Third 3D point.
    """
    return vector_angle(np.asarray(point1) - np.asarray(point2),
                        np.asarray(point3) - np.asarray(point2))


def dihedral_angle( point1: Union[List, np.ndarray],
                    point2: Union[List, np.ndarray],
                    point3: Union[List, np.ndarray],
                    point4: Union[List, np.ndarray] ) -> np.float:
    """Calculate the dihedral angle **in radiants** between 4 points.

    :param point1: First 3D point.
    :param point2: Second 3D point.
    :param point3: Third 3D point.
    :param point4: Fourth 3D point.
    """
    b0 = -1.0 * (np.asarray(point2) - np.asarray(point1))
    b1 = unit_vector(np.asarray(point3) - np.asarray(point2))
    b2 = np.asarray(point4) - np.asarray(point3)

    # vector rejections
    # v = projection of b0 onto plane perpendicular to b1
    #   = b0 minus component that aligns with b1
    # w = projection of b2 onto plane perpendicular to b1
    #   = b2 minus component that aligns with b1
    v = b0 - np.dot(b0, b1) * b1
    w = b2 - np.dot(b2, b1) * b1

    # angle between v and w in a plane is the torsion angle
    # v and w may not be normalized but that's fine since tan is y/x
    x = np.dot(v, w)
    y = np.dot(np.cross(b1.astype(np.float64), v.astype(np.float64)), w)

    return np.arctan2(y, x)


def find_transformation( vector1, vector2 ):
    """Find the transformation matrix to place ``vector1`` into ``vector2``.

    :param vector1: First 3D vector.
    :type vector1: Union[:func:`list`, :class:`~numpy.ndarray`]
    :param vector2: Second 3D vector.
    :type vector2: Union[:func:`list`, :class:`~numpy.ndarray`]

    :return: :class:`~numpy.ndarray`
    """
    v1_u = unit_vector(vector1)
    v2_u = unit_vector(vector2)

    v3 = np.cross(v1_u, v2_u)
    v3 = v3 / nl.norm(v3)
    v4 = np.cross(v3, v1_u)
    v_cos = np.dot(v2_u, v1_u)
    v_sin = np.dot(v2_u, v4)

    M1 = np.vstack([v1_u, v4, v3])

    M2 = np.array([[v_cos, v_sin, 0], [-v_sin, v_cos, 0], [0, 0, 1]])
    transformation = np.dot(M2, M1)
    transformation = np.dot(nl.inv(M1), transformation)
    return transformation


def kabsch( coordinates1: Union[List, np.ndarray],
            coordinates2: Union[List, np.ndarray] ) -> np.ndarray:
    """Find the optimal rotation to align ``coordinates1`` over ``coordinates2``.

    :param coordinates1: Matrix of 3D points. **Movable coordinates**.
    :param coordinates2: Matrix of 3D points. **Static coordinates**.

    :return: Direction Cosine Matrix for rotation
    """
    from . import moves

    # Center coordinates
    coordinates1 = moves.translate(np.copy(coordinates1), geometric_center(coordinates1))
    coordinates2 = moves.translate(np.copy(coordinates2), geometric_center(coordinates2))

    # Apply Kabsch algorithm
    V, S, Wt = np.linalg.svd(np.dot(np.transpose(coordinates2), coordinates1))

    reflect = float(str(float(np.linalg.det(V) * np.linalg.det(Wt))))
    if reflect == -1.0:
        S[-1] = -S[-1]
        V[:, -1] = -V[:, -1]

    return np.round(np.dot(V, Wt), decimals=5)


def coordinate_distance( coordinates1: Union[List, np.ndarray],
                         coordinates2: Union[List, np.ndarray],
                         method: Optional[str] = 'rmsd' ) -> np.float:
    """Calculate the distance between two sets of coordinates.

    Methods available for calculation are: **procrustes**, that assumes both entities
    are centered around the origin and **root mean square deviation** or **RMSD**.

    .. note::
        **RMSD** calculation generated by this method **DOES NOT** perform previous alignment.

    For more info check:

    * `procrustes <https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.procrustes.html>`_
    * `rmsd <https://en.wikipedia.org/wiki/Root-mean-square_deviation_of_atomic_positions>`_

    :param coordinates1: Matrix of 3D points.
    :param coordinates2: Matrix of 3D points.
    :param method: Options are **rmsd** (default) or **procrustes**.

    :return: :class:`float`

    :raises:
        :ValueError: If an unrecognized ``method`` is provided.
        :ArithmeticError: If the two coordinates do not have the same number of points.
    """
    if len(coordinates1) != len(coordinates2):
        raise ArithmeticError('The two sets of coordinates do not have the same number of points.')
    if method.lower() == 'procrustes':
        return sp.procrustes(coordinates1, coordinates2)[-1]
    elif method.lower().startswith('rms'):
        return rmsd(coordinates1, coordinates2)
    else:
        raise ValueError(f'Unknown coordinate distance method {method}.')


def rmsd( coordinates1: Union[List, np.ndarray],
          coordinates2: Union[List, np.ndarray] ) -> float:
    """Calculate RMSD between two sets of coordinates.

    .. note::
        **RMSD** calculation **DOES NOT** perform previous alignment.

    .. warning::
        This function **DOES NOT** check that the two datasets have the same size.

    :param coordinates1: First 3D Coordinate Entity.
    :param coordinates2: Second 3D Coordinate Entity.

    .. seealso::
        :meth:`.coordinate_distance`
    """
    E = 0
    for c1, c2 in zip(coordinates1, coordinates2):
        E += np.power(distance(c1, c2), 2)

    return np.sqrt(np.abs(E / len(coordinates1)))


def distance_matrix( coordinates1: Union[List, np.ndarray],
                     coordinates2: Optional[Union[List, np.ndarray]] = None,
                     **kwargs ) -> np.ndarray:
    """Generate a matrix with all vs. all distance for all availabe positions.

    All additional parameters for :func:`scipy.distance.cdist` can be provided.

    :param coordinates1: Matrix of 3D points.
    :param coordinates2: Matrix of 3D points.
    """
    coordinates2 = coordinates1 if coordinates2 is None else coordinates2
    return sp.distance.cdist(coordinates1, coordinates2, **kwargs)


def distance_array( coordinates1: Union[List, np.ndarray],
                    coordinates2: Union[List, np.ndarray] ) -> np.ndarray:
    """Generate an array with one vs. one distances.

    .. warning::
        Position of the points in the array matters here.

    :param coordinates1: Matrix of 3D points.
    :param coordinates2: Matrix of 3D points.

    :raises:
        :ArithmeticError: If the two coordinates do not have the same number of points.
    """
    if len(coordinates1) != len(coordinates2):
        raise ArithmeticError('The two sets of coordinates do not have the same number of points.')

    distance_vectors = np.diff([coordinates1, coordinates2], axis=0)[0]
    return np.linalg.norm(distance_vectors, axis=1)


def vector_angle_xyz( vector1: Union[List, np.ndarray],
                      vector2: Union[List, np.ndarray] ) -> np.ndarray:
    """Calculate the ``x``, ``y``, ``z`` radiant angles between
    two different vectors.

    :param vector1: First 3D vector.
    :param vector2: Second 3D vector.

    :return: The three angles for ``x``, ``y`` and ``z`` respectively.

    .. seealso::
        :func:`.vector_angle`
    """
    vector1 = np.asarray(vector1)
    vector2 = np.asarray(vector2)
    return np.asarray([vector_angle(vector1[[1, 2]], vector2[[1, 2]]),
                       vector_angle(vector1[[0, 2]], vector2[[0, 2]]),
                       vector_angle(vector1[[0, 1]], vector2[[0, 1]])])
