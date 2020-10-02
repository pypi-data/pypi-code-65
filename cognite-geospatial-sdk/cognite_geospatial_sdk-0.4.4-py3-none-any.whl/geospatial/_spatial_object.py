# Copyright 2020 Cognite AS
from typing import Dict

import numpy as np
from cognite.geospatial._client import FullSpatialItemDTO
from cognite.geospatial.types import Geometry

try:
    from collections.abc import Mapping  # noqa
    from collections.abc import MutableMapping  # noqa
except ImportError:
    from collections import Mapping  # noqa
    from collections import MutableMapping  # noqa


class SpatialObject(FullSpatialItemDTO, Geometry):
    def __init__(self, client=None, spatial_item: FullSpatialItemDTO = None):
        self.client = client
        self.__dict__.update(spatial_item.__dict__)

        self._layer_info = None
        self._coverage: Dict[str, object] = {}

        self.double_vector = {}
        self.integer_vector = {}
        self.boolean_vector = {}
        self.text_vector = {}

    def _set_layer_info(self, layer):
        self._layer_info = layer

    def layer_info(self):
        """Get spatial item layer.
        """
        if self._layer_info is None:
            self._layer_info = self.client.get_layer(name=self.layer)
        return self._layer_info

    def _add_double(self, name: str, vector):
        self.double_vector[name] = np.array(vector, dtype=np.double)

    def _add_integer(self, name: str, vector):
        self.integer_vector[name] = np.array(vector, dtype=np.int32)

    def _add_boolean(self, name: str, vector):
        self.boolean_vector[name] = np.array(vector, dtype=np.bool)

    def _add_text(self, name: str, value):
        self.text_vector[name] = value

    def __getitem__(self, name: str):
        if name in self.double_vector:
            return self.double_vector[name]

        if name in self.integer_vector:
            return self.integer_vector[name]

        if name in self.boolean_vector:
            return self.boolean_vector[name]

        if name in self.text_vector:
            return self.text_vector[name]

        return None

    def coverage(self, dimensional_space: str = "2d", output_crs: str = None):
        """Retrieve the coverage of the spatial object.
        Args:
            dimensional_space (str): The geometry projection of the coverage. Valid values are "2d" (default), "3d"
            output_crs (str): the crs of the coverage
        """
        if output_crs is None:
            output_crs = self.crs

        coverage_key = dimensional_space + "_" + output_crs
        if coverage_key not in self._coverage:
            coverage_obj = self.client.get_coverage(
                output_crs=output_crs, id=self.id, dimensional_space=dimensional_space
            )
            if coverage_obj is not None:
                self._coverage[coverage_key] = coverage_obj.coverage
        return self._coverage[coverage_key]

    def delete(self) -> bool:
        """Delete spatial item.
        """
        item = self.client.delete_spatial(id=self.id)
        return item is not None

    def get(self):
        """ Get numpy arrays of x,y,z if the layer is raster/seismic/horizon. Otherwise, get geometry in the form of wkt
        """
        x_name, y_name, z_name = self._xyz()
        if self.layer == "raster" or self.layer == "seismic" or self.layer == "horizon":
            active = self.__getitem__("active")
            x = self.__getitem__(x_name)
            y = self.__getitem__(y_name)
            z = self.__getitem__(z_name)
            if z is None:
                data = np.stack((x, y), axis=-1)
            else:
                data = np.stack((x, y, z), axis=-1)
            if active is None:
                return data
            active = active[: len(data)]
            return data[active]
        else:
            return self.geometry.wkt

    def height(self):
        """ Get the difference between maximum and minimum inline
        """
        rows = self._row_min_max()
        return self._get_side_size(rows, self._height_name())

    def width(self):
        """ Get the difference between maximum and minimum cross-line
        """
        columns = self._column_min_max()
        return self._get_side_size(columns, self._width_name())

    def _get_side_size(self, min_max, size_name):
        if min_max is not None:
            min_ = self.__getitem__(min_max[0])
            max_ = self.__getitem__(min_max[1])
            if min_ is not None and max_ is not None:
                return int(max_) - int(min_) + 1
        elif size_name is not None:
            return self.__getitem__(size_name)
        return None

    def _row_min_max(self):
        if self.layer == "seismic":
            return ("iline_min", "iline_max")
        return None

    def _column_min_max(self):
        if self.layer == "seismic":
            return ("xline_min", "xline_max")
        return None

    def _xyz(self):
        return ("x", "y", "z")

    def _row_column(self):
        if self.layer == "horizon":
            row_name = "row"
            column_name = "column"
        elif self.layer == "seismic":
            row_name = "xline"
            column_name = "iline"
        return (row_name, column_name)

    def _height_name(self):
        if self.layer == "horizon":
            return "height"
        return None

    def _width_name(self):
        if self.layer == "horizon":
            return "width"
        return None

    def grid(self):
        """ Get the grid representation if the layer is raster/seismic/horizon
        """
        row_name, column_name = self._row_column()
        x_name, y_name, z_name = self._xyz()

        if self.layer == "raster" or self.layer == "seismic" or self.layer == "horizon":
            active = self.__getitem__("active")
            x = self.__getitem__(x_name)
            y = self.__getitem__(y_name)
            z = self.__getitem__(z_name)
            if z is None:
                points = np.stack((x, y), axis=-1)
            else:
                points = np.stack((x, y, z), axis=-1)
            width = self.width()
            height = self.height()

            if active is None:
                rows = self.__getitem__(row_name)
                columns = self.__getitem__(column_name)

                if rows is None or columns is None:
                    return None
                data = np.ndarray(shape=(height, width, points.shape[1]), dtype=np.double)
                for i in range(len(points)):
                    r = rows[i] - rows.min()
                    c = columns[i] - columns.min()
                    data[r, c] = points[i]
            else:
                data = np.ndarray(shape=(width, height, points.shape[1]), dtype=np.double)
                size = len(active)
                active_indx = np.argwhere(active[:size] == True)  # noqa: E712
                for i in active_indx:
                    r = int(i % height)
                    c = int((i - r) / height)
                    data[c, r] = points[i]

            return data
        return None

    def __str__(self):
        return f"id: {self.id}\nexternal_id: {self.external_id}\nname: {self.id}\nlayer: {self.layer}\ncrs: {self.crs}"
