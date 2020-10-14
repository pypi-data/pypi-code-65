# -*- coding: utf-8 -*-
"""
.. codeauthor:: Jaume Bonet <jaume.bonet@gmail.com>

.. affiliation::
    Structural BioInformatics Lab <sbi.upf.edu>
    Baldo Oliva <baldo.oliva@upf.edu>

.. module:: structure.geometry.Frame3D
   :platform: Unix, Windows
   :synopsis: Classes to which geometry is applied.

.. class:: structure.geometry.Series3D
   :synopsis: :class:`~pandas.Series`-like object with 3D geometrical properties.
.. class:: structure.geometry.Frame3D
   :synopsis: :class:`~pandas.DataFrame`-like object with 3D geometrical properties.
"""
# Standard Libraries
from typing import (
    List,
    Optional,
    TypeVar,
    Union)

# External Libraries
import numpy as np
import pandas as pd

# This Library
from SBI.core import core
from . import basics, moves


__all__ = ['Series3D', 'Frame3D']

##
# Local Globals: Based on hardcoded naming system from the PDB.
##
PDB_MODEL_NUM_ = 'pdbx_PDB_model_num'
COORD_TAGS_ = ['Cartn_x', 'Cartn_y', 'Cartn_z']

S3 = TypeVar('S3', bound='Series3D')
F3 = TypeVar('F3', bound='Frame3D')


class Series3D( pd.Series ):
    """General :class:`~pandas.Series`-like object with 3D geometrical properties.

    .. admonition:: To Developers

        This object should not be aware of any biological context, with the exception of
        ``pdbx_PDB_model_num``, which is required to assert which coordinates are used.

    Description
    ===========

    By all intents and purposes, this is a ``3D point`` with extra information.

    Covered Fields from the Protein Data Bank
    =========================================

    * `Cartn_x <http://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v40.dic/Items/_atom_site.Cartn_x.html>`_
    * `Cartn_y <http://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v40.dic/Items/_atom_site.Cartn_y.html>`_
    * `Cartn_z <http://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v40.dic/Items/_atom_site.Cartn_z.html>`_

    .. seealso::
        :class:`.Frame3D`
    """
    ###
    # Public Properties
    ###
    @property
    def x( self ) -> np.float32:
        """Value of the **X** axis.

        .. seealso::
            :meth:`.Series3D.y`
            :meth:`.Series3D.z`
            :meth:`.Series3D.coordinates`
        """
        return self[self._coord_tags[0]]

    @property
    def y( self ) -> np.float32:
        """Value of the **Y** axis.

        .. seealso::
            :meth:`.Series3D.x`
            :meth:`.Series3D.z`
            :meth:`.Series3D.coordinates`
        """
        return self[self._coord_tags[1]]

    @property
    def z( self ) -> np.float32:
        """Value of the **Z** axis.

        .. seealso::
            :meth:`.Series3D.x`
            :meth:`.Series3D.y`
            :meth:`.Series3D.coordinates`
        """
        return self[self._coord_tags[2]]

    @property
    def coordinates( self ) -> np.ndarray:
        """Values for the **X**, **Y** and **Z** axis.

        .. seealso::
            :meth:`.Series3D.x`
            :meth:`.Series3D.y`
            :meth:`.Series3D.z`
        """
        return self[self._coord_tags].values

    ###
    # Geometric Query Methods
    ###
    def distance( self, other: Optional[Union[S3, np.ndarray]] = None ) -> np.float:
        """Euclidean distance between two coordinates.

        :param other: Target to which the distance is measured.
        """
        if other is None or isinstance(other, np.ndarray):
            return basics.distance(self.coordinates, other)
        elif isinstance(other, Series3D):
            return basics.distance(self.coordinates, other.coordinates)
        else:
            return NotImplementedError()

    ###
    # Private Properties
    ###
    @property
    def _coord_tags( self ) -> List[str]:
        """Identifiers for the columns containing the X, Y, Z coordinates.
        """
        return COORD_TAGS_

    ###
    # Pandas Specificities
    ###
    @property
    def _constructor( self ) -> S3:
        return Series3D

    @property
    def _constructor_expanddim( self ) -> F3:
        return Frame3D

    def __finalize__( self, other, method=None, **kwargs ):
        if method == 'slice':
            # Avoid columns becoming Series3D
            if not isinstance(self.name, (int, np.int64)):
                return pd.Series(self)
        return Series3D(super(Series3D, self).__finalize__(other, method, **kwargs))


class Frame3D( pd.DataFrame ):
    """General :class:`~pandas.DataFrame`-derived class from which all 3D structure objects inherit.

    .. admonition:: To Developers

        This object should not be aware of any biological context, with the exception of
        ``pdbx_PDB_model_num``, which is required to assert which coordinates are used.

    Description
    ===========

    :class:`.Frame3D` covers two very specific properties of Coordinate Entities.

    Geometric Applications
    ----------------------

    All structure-based objects should behave the same when challenged with a geometrical application.
    As such, geometry is stablished in :class:`.Frame3D`, at the base of the class tree. If new geometric
    behaviours need to be implemented, this is the place to go.

    Logically specif geometric behaviour should be overwritten when needed in the required sub-class.

    Structure Model
    ---------------

    .. note::
        Depends on the :ref:`global configuration options <configuration>` ``structure.model``.

    Refers to the **MODEL** record, which specifies the model serial number when multiple models of the same
    structure are presented in a single coordinate entry, as is often the case with structures determined by
    [NMR](https://en.wikipedia.org/wiki/Nuclear_magnetic_resonance_spectroscopy). Do not confuse this with
    **OCCUPANCY**, which references [the slight packing differences between crystal
    cells](https://pdb101.rcsb.org/learn/guide-to-understanding-pdb-data/dealing-with-coordinates).

    The selection of the working model is performed through the property :meth:`.Frame3D._current_model`.
    Effectively, to make sure that any selection or transformation is performed only on the selected model,
    one can internaly make a copy of the model of interest.

    To avoid state confusion, most functions depend on this feature, and they are labeled appropiately.

    See :ref:`working with NMR models <>` for further examples.

    Covered Fields from the Protein Data Bank
    =========================================

    * `pdbx_PDB_model_num <http://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v40.dic/Items/_atom_site.pdbx_PDB_model_num.html>`_
    * `Cartn_x <http://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v40.dic/Items/_atom_site.Cartn_x.html>`_
    * `Cartn_y <http://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v40.dic/Items/_atom_site.Cartn_y.html>`_
    * `Cartn_z <http://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v40.dic/Items/_atom_site.Cartn_z.html>`_


    """
    ###
    # Public Properties
    ###
    @property
    def x( self ) -> np.ndarray:
        """All values of the **X** axis.

        .. note::
            Depends on the :ref:`global configuration option <configuration>` ``structure.model``.

        .. seealso::
            :meth:`.Frame3D.y`
            :meth:`.Frame3D.z`
            :meth:`.Frame3D.coordinates`
        """
        self._check_coordinate_tags()
        return self._current_model[self._coord_tags[0]].values

    @property
    def y( self ) -> np.ndarray:
        """All values of the **Y** axis.

        .. note::
            Depends on the :ref:`global configuration option <configuration>` ``structure.model``.

        .. seealso::
            :meth:`.Frame3D.x`
            :meth:`.Frame3D.z`
            :meth:`.Frame3D.coordinates`
        """
        self._check_coordinate_tags()
        return self._current_model[self._coord_tags[1]].values

    @property
    def z( self ) -> np.ndarray:
        """All values of the **Z** axis.

        .. note::
            Depends on the :ref:`global configuration option <configuration>` ``structure.model``.

        .. seealso::
            :meth:`.Frame3D.x`
            :meth:`.Frame3D.y`
            :meth:`.Frame3D.coordinates`
        """
        self._check_coordinate_tags()
        return self._current_model[self._coord_tags[2]].values

    @property
    def coordinates( self ) -> np.ndarray:
        """All values for the **X**, **Y** and **Z** axis.

        .. note::
            Depends on the :ref:`global configuration options <configuration>` ``structure.model``.

        .. seealso::
            :meth:`.Frame3D.x`
            :meth:`.Frame3D.y`
            :meth:`.Frame3D.z`
        """
        self._check_coordinate_tags()
        return self._current_model[self._coord_tags].values

    @property
    def model_ids( self ) -> List[int]:
        """List the IDs of the models in the Coordinate Entity.
        """
        if PDB_MODEL_NUM_ not in self.columns:
            return [1, ]
        return list([int(x) for x in self[PDB_MODEL_NUM_].unique()])

    @property
    def model_count( self ) -> int:
        """Counts the number of models in the Coordinate Entity.
        """
        return len(self.model_ids)

    ###
    # Geometryc Booleans
    ###
    @property
    def is_centered( self ):
        """Evaluate if the geometric center of the coordinate entity matches the center of coordinates.

        .. note::
            Depends on the :ref:`global configuration options <configuration>` ``structure.model``.

        :return: :class:`bool`

        .. seealso::
            :meth:`.Frame3D.geometric_center`
        """
        return np.allclose(np.zeros(3, float), self.geometric_center(), atol=1.e-4)

    ###
    # General Methods
    ###
    def current_model( self, inplace: Optional[bool] = None ) -> F3:
        """Provide only the current working model.

        .. note::
            Depends on the :ref:`global configuration options <configuration>` ``system.inplace``.
            Depends on the :ref:`global configuration options <configuration>` ``structure.model``.

        :param bool inplace: When True, changes are applied to the object itself.
            When False, a new copy object is returned with the applied changes.

        :return: Frame3D
        """
        return self._inplace(self._current_model, inplace)

    ###
    # Geometric Query Methods
    ###
    def geometric_center( self ) -> np.ndarray:
        """Get the geometric center of the coordinate entity.

        .. note::
            Depends on the :ref:`global configuration options <configuration>` ``structure.model``.
        """
        return basics.geometric_center(self.coordinates)

    def eigenvectors( self, module: Optional[float] = 2.0 ) -> np.ndarray:
        """Return the three eigenvectors defining the coordinate entity.

        .. note::
            Depends on the :ref:`global configuration options <configuration>` ``structure.model``.

        :param float module: Module for the vectors.

        :return: 3 vectors, ordered as *perpendicular*, *side* and *major* eigenvectors. Each vector contains 3 points:
            ``starting``, ``center`` and ``end`` points to match the expected module length, being ``center`` the point
            shared between the three and the distance between ``starting`` and ``end`` the expected module.
        """
        return basics.eigenvectors(self.coordinates, module)

    def distance_matrix( self, other=None, **kwargs ):
        """Generate a matrix with all vs. all distance for all availabe positions.

        Optional parameters can be provided for :func:`scipy.distance.cdist`.

        .. note::
            Depends on the :ref:`global configuration options <configuration>` ``structure.model``.

        :param other: Other container against which to compare.
        :type other: Optional[:class:`.Frame3D`]

        :return: :class:`~numpy.ndarray`
        """
        other = self if other is None else other
        return basics.distance_matrix(self.coordinates, other.coordinates, **kwargs)

    def distance_array( self, other ):
        """Generate an array with one vs. one distances.

        .. warning::
            Order of the points in the array matters here.

        .. note::
            Depends on the :ref:`global configuration options <configuration>` ``structure.model``.

        :param other: Other container against which to compare.
        :type other: Optional[:class:`.Frame3D`]

        :return: :class:`~numpy.ndarray`

        :raises:
            :ArithmeticError: If the two coordinate entities do not have the same number of points.
        """
        return basics.distance_array(self.coordinates, other.coordinates)

    ###
    # Geometry Transformation Methods
    ###
    def translate( self, vector=None, inplace=None ):
        """Translate the coordinate entity according to the provided vector.

        .. note::
            Depends on the :ref:`global configuration options <configuration>` ``system.inplace``.
            Depends on the :ref:`global configuration options <configuration>` ``structure.model``.

        :param vector: 3D vector to apply to the Frame3D.
        :param vector: Union[:func:`list`, :class:`~numpy.ndarray`, :class:`dict`]
        :param bool inplace: When :data:`True`, changes are applied
            to the object itself. When :data:`False`, a new copy object is
            returned with the applied changes.

        :return: :class:`.Frame3D`

        :raise:
            :ValueError: If input vector has the wrong dimensionality.

        .. seealso::
            :meth:`.Frame3D.translate_to_origin`
        """
        # Process dictionary if that is the input
        if isinstance(vector, dict):
            vector = [vector.get('x', 0), vector.get('y', 0), vector.get('z', 0)]

        # Apply: The copy makes sure that the coordinates of other models remain the same.
        df = self.copy()
        dm = self.current_model(False).copy()
        dm[dm._coord_tags] = moves.translate(dm.coordinates, vector)
        df.update(dm)

        # Inplace decision
        return self._inplace(df, inplace)

    def translate_to_origin( self, inplace=None ):
        """Translate the coordinate entity to the center of coordinates.

        This is a specific application of :meth:`.Frame3D.translate`.

        .. note::
            Depends on the :ref:`global configuration options <configuration>` ``system.inplace``.
            Depends on the :ref:`global configuration options <configuration>` ``structure.model``.

        :param bool inplace: When :data:`True`, changes are applied
            to the object itself. When :data:`False`, a new copy object is
            returned with the applied changes.

        :return: :class:`.Frame3D`

        .. seealso::
            :meth:`.Frame3D.translate`
        """
        return self.translate(-self.geometric_center(), inplace=inplace)

    def rotate( self, matrix=None, center=None, inplace=None ):
        """Rotate the coordinate entity over a given point.

        .. note::
            Depends on the :ref:`global configuration options <configuration>` ``system.inplace``.
            Depends on the :ref:`global configuration options <configuration>` ``structure.model``.

        :param matrix: 3D matrix (3x3) to apply to the coordinate entity.
        :param matrix: :param matrix: Optional[Union[:class:`~numpy.ndarray`,
            :class:`~scipy.spatial.transform.Rotation`]]
        :param center: Point over which rotate. Default is the center of coordinates (``[0., 0., 0.]``).
        :param center: Union[:func:`list`, :class:`~numpy.ndarray`]
        :param bool inplace: When :data:`True`, changes are applied
            to the object itself. When :data:`False`, a new copy object is
            returned with the applied changes.

        :return: :class:`.Frame3D`

        :raise:
            :ValueError: If ``matrix`` does not have the right dimensionality.

        .. seealso::
            :meth:`.Frame3D.rotate_euler`
            :meth:`.Frame3D.spin`
            :meth:`.Frame3D.spin_euler`
        """
        # Apply
        df = self.copy()
        dm = self.current_model(False).copy()
        dm[dm._coord_tags] = moves.rotate(dm.coordinates, matrix, center)
        df.update(dm)

        # Inplace decision
        return self._inplace(df, inplace)

    def spin( self, matrix=None, inplace=None ):
        """Rotate the coordinate entity over its center of mass.

        This is a specific application of :meth:`.Frame3D.rotate`.

        .. note::
            Depends on the :ref:`global configuration options <configuration>` ``system.inplace``.
            Depends on the :ref:`global configuration options <configuration>` ``structure.model``.

        :param matrix: 3D matrix (3x3) to apply to the coordinate entity.
        :param matrix: :param matrix: Optional[Union[:class:`~numpy.ndarray`,
            :class:`~scipy.spatial.transform.Rotation`]]
        :param bool inplace: When :data:`True`, changes are applied
            to the object itself. When :data:`False`, a new copy object is
            returned with the applied changes.

        :return: :class:`.Frame3D`

        :raise:
            :AttributeError: If ``matrix`` does not have the right dimensionality.

        .. seealso::
            :meth:`.Frame3D.rotate`
            :meth:`.Frame3D.rotate_euler`
            :meth:`.Frame3D.spin_euler`
        """
        return self.rotate(matrix, self.geometric_center(), inplace)

    def rotate_euler( self, x=0, y=0, z=0, center=None, degrees=False, inplace=None ):
        """Rotate the coordinate entity over a given point.

        .. note::
            Depends on the :ref:`global configuration options <configuration>` ``system.inplace``.
            Depends on the :ref:`global configuration options <configuration>` ``structure.model``.

        ..warning::
            Rotating multiple eugler angles simultaneusly is counter intuitive. Provide one angle at a time.

        :param float x: Degrees to rotate in the global ``x`` axis.
        :param float y: Degrees to rotate in the global ``y`` axis.
        :param float z: Degrees to rotate in the global ``z`` axis.
        :param center: Point over which rotate. Default is the center of coordinates (``[0., 0., 0.]``).
        :param bool degrees: Use degrees instead of radiants.
        :param bool inplace: When :data:`True`, changes are applied
            to the object itself. When :data:`False`, a new copy object is
            returned with the applied changes.

        :return: :class:`.Frame3D`

        .. seealso::
            :meth:`.Frame3D.rotate`
            :meth:`.Frame3D.spin`
            :meth:`.Frame3D.spin_euler`
        """
        # Apply
        df = self.copy()
        dm = self.current_model(False).copy()
        dm[dm._coord_tags] = moves.rotate_euler(dm.coordinates, x, y, z, center, degrees)
        df.update(dm)

        # Inplace decision
        return self._inplace(df, inplace)

    def spin_euler( self, angle, axis, degrees=False, inplace=None ):
        """Rotate the coordinate entity over its center of mass over a given axis.

        .. note::
            Depends on the :ref:`global configuration options <configuration>` ``system.inplace``.
            Depends on the :ref:`global configuration options <configuration>` ``structure.model``.

        :param float angle: Euler angle of how much to turn.
        :param str axis: Axis over which the rotation is to be performed. Options are
            **perpendicular**, **side** and **major** for the object's eigenvectors. Or **x**, **y**
            and **z** for the global axes.
        :param bool degrees: Use degrees instead of radiants.
        :param bool inplace: When :data:`True`, changes are applied
            to the object itself. When :data:`False`, a new copy object is
            returned with the applied changes.

        :return: :class:`.Frame3D`

        :raise:
            :ValueError: If an unknown ``axis`` value is provided.

        .. seealso::
            :meth:`.Frame3D.rotate`
            :meth:`.Frame3D.rotate_euler`
            :meth:`.Frame3D.spin`
        """
        gax = {'x': 0, 'y': 0, 'z': 0}
        pax = {'perpendicular': moves.yaw, 'side': moves.pitch, 'major': moves.roll}
        if axis.lower() in gax:
            gax[axis.lower()] = angle
            return self.rotate_euler(**gax, center=self.geometric_center(), degrees=degrees, inplace=inplace)
        elif axis.lower() in pax:
            # Apply
            df = self.copy()
            dm = self.current_model(False).copy()
            dm[dm._coord_tags] = pax[axis](dm.coordinates, angle, degrees)
            df.update(dm)

            # Inplace decision
            return self._inplace(df, inplace)
        else:
            raise ValueError(f'Unknown axis id {axis}')

    ###
    # Private Checks
    ###
    def _check_coordinate_tags( self ):
        if not set(self._coord_tags).issubset(set(self.columns)):
            raise KeyError(f'Frame3D requires columns {self._coord_tags}')

    ###
    # Private Properties
    ###
    @property
    def _coord_tags( self ):
        """Identifiers for the columns containing the X, Y, Z coordinates.
        """
        return COORD_TAGS_

    @property
    def _current_model( self ):
        # !! Extra Complexity Issue !!
        # ----------------------------
        # Some structure DO NOT have MODEL==1
        # This is why the default value of structure.model is -1, to capture those.
        # See [PDB_RULE: 1KLD; FORMAT: ALL], which starts in MODEL 18.
        cm = core.get_option('structure', 'model')
        # Cases without model specification
        if cm == 0 or PDB_MODEL_NUM_ not in self.columns:
            return self
        cm = cm if cm > 0 else self[PDB_MODEL_NUM_].min()
        return self[self[PDB_MODEL_NUM_] == cm]

    ###
    # Magic Methods
    ###
    def __eq__( self, other ):
        """Evaluate if the positions of two coordinate entities are the same.

        .. note::
            Depends on the :ref:`global configuration options <configuration>` ``structure.model``.

        :param other: Object to compare with.
        :type other: :class:`.Frame3D`

        :return: :class:`bool`

        :raises:
            :NotImplementedError: If an unexpected object type is provided.
        """
        if not isinstance(other, Frame3D):
            raise NotImplementedError('Unable to compare incompatible objects')
        return np.allclose(other.coordinates, self.coordinates, atol=0.00001)

    def __add__( self, other ):
        """Implements ``inplace=False`` :meth:`.Frame3D.translate`
        """
        return self.translate( other, inplace=False )

    def __iadd__( self, other ):
        """Implements ``inplace=True`` :meth:`.Frame3D.translate`
        """
        return self.translate( other, inplace=True )

    def __mul__( self, other ):
        """Implements ``inplace=False`` :meth:`.Frame3D.rotation`
        """
        return self.rotate( other, inplace=False)

    def __imul__( self, other ):
        """Implements ``inplace=False`` :meth:`.Frame3D.rotation`
        """
        return self.rotate( other, inplace=True)

    def __str__(self):
        return pd.DataFrame(self).__str__()

    def _repr_html_( self ):
        return pd.DataFrame(self)._repr_html_()

    ###
    # Pandas Specificities
    ###
    def _inplace( self, df, inplace, verify_is_copy=True ):
        inplace = core.get_option('system', 'inplace') if inplace is None else inplace
        if inplace:
            self._update_inplace(df, verify_is_copy)
            return self
        else:
            return df

    @property
    def _constructor( self ):
        return Frame3D

    @property
    def _constructor_sliced( self ):
        def f(*args, **kwargs):
            return Series3D(*args, **kwargs).__finalize__(self, method='sliced')
        return f

    def __finalize__( self, other, method=None, **kwargs ):
        if method == 'concat':
            if not isinstance(self.index, pd.core.index.MultiIndex):
                return self.reset_index()
        return Frame3D(super(Frame3D, self).__finalize__(other, method, **kwargs))
