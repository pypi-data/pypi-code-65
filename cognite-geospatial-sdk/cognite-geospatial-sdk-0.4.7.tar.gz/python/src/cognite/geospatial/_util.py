# Copyright 2020 Cognite AS

import sys

import numpy as np


def geom_to_arr(geom):
    try:
        xy = getattr(geom, "xy", None)
    except NotImplementedError:
        xy = None

    if xy is not None:
        return np.column_stack(xy)
    if hasattr(geom, "array_interface"):
        data = geom.array_interface()
        return np.array(data["data"]).reshape(data["shape"])[:, :2]
    arr = geom.array_interface_base["data"]

    if (len(arr) % 2) != 0:
        arr = arr[:-1]
    return np.array(arr).reshape(-1, 2)


def geom_to_array(geom):
    if geom.geom_type == "Point":
        return np.array([[geom.x, geom.y]])
    if hasattr(geom, "exterior"):
        if geom.exterior is None:
            xs, ys = np.array([]), np.array([])
        else:
            xs = np.array(geom.exterior.coords.xy[0])
            ys = np.array(geom.exterior.coords.xy[1])
    elif geom.geom_type in ("LineString", "LinearRing"):
        return geom_to_arr(geom)
    elif geom.geom_type == "MultiPoint":
        arrays = []
        for g in geom:
            if g.geom_type == "Point":
                arrays.append(np.array(g.xy).T)
        return np.concatenate(arrays) if arrays else np.array([])
    else:
        arrays = []
        for g in geom:
            arrays.append(geom_to_arr(g))
            arrays.append(np.array([[np.nan, np.nan]]))
        return np.concatenate(arrays[:-1]) if arrays else np.array([])
    return np.column_stack([xs, ys])


def holo_plot_geometry(geom, label=None):
    if "holoviews" in sys.modules:
        import holoviews as hv

        if geom.geom_type == "Point":
            return hv.Points([[geom.x, geom.y]], label=label)
        elif geom.geom_type == "MultiPoint":
            return hv.Points(geom_to_array(geom), label=label)
        elif geom.geom_type in ("LineString", "LinearRing"):
            coordinate = geom_to_array(geom)
            return hv.Path({"x": coordinate[:, 0], "y": coordinate[:, 1]}, ["x", "y"], label=label)
        elif geom.geom_type == "Polygon":
            coordinate = geom_to_array(geom)
            return hv.Polygons([{("x", "y"): coordinate}])
        elif geom.geom_type == "MultiPolygon":
            return hv.Polygons([{("x", "y"): geom_to_array(g)} for g in geom], label=label)
        else:
            plots = None
            for g in geom:
                if plots is None:
                    plots = holo_plot_geometry(g)
                else:
                    plots = plots * holo_plot_geometry(g)
            return plots

    return None


def plot_geometry(geometry, label=None):
    if geometry is not None:
        return holo_plot_geometry(geometry, label=label)

    return None
