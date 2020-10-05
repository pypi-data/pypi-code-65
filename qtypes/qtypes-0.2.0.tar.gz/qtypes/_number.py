__all__ = ["Number", "NumberLimits"]


import math

from qtpy import QtCore, QtGui, QtWidgets

from ._base import Base
from ._units import converter
from ._units import dicts


class NumberLimits(Base):
    def __init__(self, min_value=-1e6, max_value=1e6, units=None):
        """
        not appropriate for use as a gui element - only for backend use
        units must never change for this kind of object
        """
        super().__init__(value=[min_value, max_value])
        self.units = units

    def get(self, output_units="same"):
        min_value, max_value = self.value.get()
        if output_units == "same":
            pass
        else:
            min_value = converter(min_value, self.units, output_units)
            max_value = converter(max_value, self.units, output_units)
        # ensure order
        min_value, max_value = [
            min([min_value, max_value]),
            max([min_value, max_value]),
        ]
        return [min_value, max_value]

    def set(self, min_value, max_value, input_units="same"):
        if input_units == "same":
            pass
        else:
            min_value = converter(min_value, input_units, self.units)
            max_value = converter(max_value, input_units, self.units)
        # ensure order
        min_value, max_value = [
            min([min_value, max_value]),
            max([min_value, max_value]),
        ]
        self.value.set([min_value, max_value])
        self.updated.emit()


class Number(Base):
    units_updated = QtCore.Signal()
    qtype = "number"

    def __init__(
        self,
        value=float("nan"),
        single_step=1.0,
        decimals=3,
        limits=None,
        units=None,
        *args,
        **kwargs
    ):
        super().__init__(value=value, *args, **kwargs)
        self.disabled_units = False
        self.single_step = single_step
        self.decimals = decimals
        self.set_control_steps(single_step, decimals)
        # units
        self.units = units
        self.units_kind = None
        for k, dic in dicts.items():
            if self.units in dic.keys():
                self.units_dic = dic
                self.units_kind = k
        # limits
        self.limits = limits
        if self.limits is None:
            self.limits = NumberLimits()
        if self.units is None:
            self.limits.units = None
        if self.units is not None and self.limits.units is None:
            self.limits.units = self.units
        self._set_limits()
        self.limits.updated.connect(self._set_limits)

    def _set_limits(self):
        min_value, max_value = self.limits.get()
        limits_units = self.limits.units
        min_value = converter(min_value, limits_units, self.units)
        max_value = converter(max_value, limits_units, self.units)
        # ensure order
        min_value, max_value = [
            min([min_value, max_value]),
            max([min_value, max_value]),
        ]
        if self.has_widget:
            self.widget.setMinimum(min_value)
            self.widget.setMaximum(max_value)
            if not self.disabled:
                self.set_tool_tip(
                    "min: " + str(min_value) + "\n" + "max: " + str(max_value)
                )

    def convert(self, destination_units):
        # value
        self.value.lock()
        old_val = self.value.get()
        new_val = converter(old_val, self.units, str(destination_units))
        self.value.unlock()
        self.value.set(new_val)
        # commit and signal
        self.units = str(destination_units)
        self._set_limits()
        self.units_updated.emit()
        self.updated.emit()

    def get(self, output_units="same"):
        value = super().__call__()
        if output_units == "same":
            pass
        else:
            value = converter(value, self.units, output_units)
        return value

    def set_control_steps(self, single_step=None, decimals=None):
        limits = [self.single_step, self.decimals]
        inputs = [single_step, decimals]
        widget_methods = ["setSingleStep", "setDecimals"]
        for i in range(len(limits)):
            if not inputs[i] is None:
                limits[i] = inputs[i]
            if self.has_widget:
                getattr(self.widget, widget_methods[i])(limits[i])

    def set_disabled_units(self, disabled):
        self.disabled_units = bool(disabled)
        if self.has_widget:
            self.units_widget.setDisabled(self.disabled_units)

    def set_units(self, units):
        if self.has_widget:
            allowed = [
                self.units_widget.itemText(i) for i in range(self.units_widget.count())
            ]
            index = allowed.index(units)
            self.units_widget.setCurrentIndex(index)
        else:
            self.convert(units)

    def set_widget(self):
        # special value text is displayed when widget is at minimum
        if math.isnan(self.value.get()):
            self.widget.setSpecialValueText("nan")
            self.widget.setValue(self.widget.minimum())
        else:
            self.widget.setSpecialValueText("")
            self.widget.setValue(self.value.get())

    def give_control(self, control_widget):
        self.widget = control_widget
        # set values
        min_value, max_value = self.limits.get()
        self.widget.setMinimum(min_value)
        self.widget.setMaximum(max_value)
        self.widget.setDecimals(self.decimals)
        self.widget.setSingleStep(self.single_step)
        self.set_widget()
        # connect signals and slots
        self.updated.connect(self.set_widget)
        self.widget.editingFinished.connect(lambda: self.set(self.widget.value()))
        # finish
        self.widget.setToolTip(self.tool_tip)
        self.widget.setDisabled(self.disabled)
        self.has_widget = True
        self._set_limits()

    def give_units_combo(self, units_combo_widget):
        self.units_widget = units_combo_widget
        # add items
        unit_types = list(self.units_dic.keys())
        self.units_widget.addItems(unit_types)
        # set current item
        self.units_widget.setCurrentIndex(unit_types.index(self.units))
        # associate update with conversion
        self.units_widget.currentIndexChanged.connect(
            lambda: self.convert(self.units_widget.currentText())
        )
        # finish
        self.units_widget.setDisabled(self.disabled_units)

    def set(self, value, units="same"):
        if units == "same":
            pass
        else:
            value = converter(value, units, self.units)
        super().set(value)
