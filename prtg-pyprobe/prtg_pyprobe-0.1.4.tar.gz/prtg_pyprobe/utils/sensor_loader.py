import importlib
import pkgutil

from prtg_pyprobe.sensors.sensor import SensorBase


def load_sensor_modules(sensor_path="sensors") -> dict:
    # plugin discovery with enforcing of naming convention
    usable_plugins = {}
    discovered_plugins = {
        name: importlib.import_module(f"prtg_pyprobe.sensors.{name}")
        for finder, name, ispkg in pkgutil.iter_modules([sensor_path])
        if name.startswith("sensor_")
    }

    # check if the Plugin is inheriting from a common base class
    for name, mod in discovered_plugins.items():
        if issubclass(mod.Sensor, SensorBase):
            usable_plugins[name] = mod
    return discovered_plugins


def create_sensor_objects(*args, **kwargs) -> list:
    # creating objects from loaded modules
    obj_list = []
    for name, module in load_sensor_modules(*args, **kwargs).items():
        obj_list.append(module.Sensor())
    return obj_list
