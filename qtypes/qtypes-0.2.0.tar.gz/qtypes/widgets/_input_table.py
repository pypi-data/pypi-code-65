__all__ = ["InputTable"]


import os
import collections
from qtpy import QtWidgets, QtGui

from ._spin_box import DoubleSpinBox


# size notes for input table
#   all rows have height of exactly 25
#   all rows have total width of 300


class InputTable(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setFixedWidth(300)
        self.row_number = 0
        self.controls = []
        self._objs = {}

    def __getattr__(self):
        raise NotImplementedError

    def __getitem__(self, key):
        return self._objs[key]

    def __setitem__(self, value):
        raise NotImplementedError

    def append(self, obj, label=None):
        if label is None:
            label = obj.name
        # type
        if obj is None:
            _type = "heading"
            self._append_heading(label)
        else:
            _type = obj.qtype
            setattr(self, obj.name, obj)
            getattr(self, f"_append_{_type}")(label, obj)
            self._objs[obj.name] = obj

    def _append_heading(self, label):
        row_layout = self._get_row_layout(label)
        row_layout.addStretch(1)

    def _append_number(self, label, obj):
        layout = self._get_row_layout(label)
        # control
        control = DoubleSpinBox()
        if obj.disabled:
            control.setDisabled(True)
        obj.give_control(control)
        layout.addWidget(control)
        control.setFixedHeight(25)
        # units combobox
        if obj.units_kind is None:
            control.setFixedWidth(150)
        else:
            control.setFixedWidth(100)
            units = QtWidgets.QComboBox()
            units.setFixedHeight(25)
            units.setFixedWidth(50)
            units.setStyleSheet("margin-right:5px")
            layout.addWidget(units)
            obj.give_units_combo(units)
        # finish
        self.controls.append(control)

    def _append_string(self, label, obj):
        layout = self._get_row_layout(label)
        # control
        control = QtWidgets.QLineEdit()
        control.setFixedWidth(150)
        control.setFixedHeight(25)
        control.setStyleSheet("margin-right:5px")
        obj.give_control(control)
        layout.addWidget(control)
        # finish
        self.controls.append(control)

    def _append_enum(self, label, obj):
        layout = self._get_row_layout(label)
        # control
        control = QtWidgets.QComboBox()
        control.setFixedWidth(150)
        control.setFixedHeight(25)
        obj.give_control(control)
        layout.addWidget(control)
        # finish
        self.controls.append(control)

    def _append_bool(self, label, obj):
        layout = self._get_row_layout(label)
        # control
        control = QtWidgets.QCheckBox()
        style = "QCheckBox::indicator {width:25px;height: 25px;}"
        control.setStyleSheet(style)
        obj.give_control(control)
        layout.addWidget(control)
        layout.addStretch()
        # finish
        self.controls.append(control)

    def _append_filepath(self, label, obj):
        layout = self._get_row_layout(label)
        # layout
        container_widget = QtWidgets.QWidget()
        container_widget.setLayout(QtWidgets.QHBoxLayout())
        container_widget.layout().setContentsMargins(0, 0, 0, 0)
        # push button
        load_button = QtWidgets.QPushButton("Load")
        load_button.setFixedHeight(25)
        load_button.setFixedWidth(40)
        container_widget.layout().addWidget(load_button)
        obj.give_button(load_button)
        # stretch
        container_widget.layout().addStretch(1)
        # display
        display = QtWidgets.QLineEdit()
        # display.setDisabled(True)
        display.setReadOnly(True)
        load_button.setFixedHeight(25)
        display.setFixedWidth(104)
        container_widget.layout().addWidget(display)
        obj.give_control(display)
        # finish
        layout.addWidget(container_widget)
        self.controls.append(container_widget)

    def extend(self):
        raise NotImplementedError

    def _get_row_layout(self, label):
        # create layout
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # add heading
        heading = QtWidgets.QLabel(label)
        heading.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        heading.setFixedHeight(25)
        heading.setFixedWidth(150)
        heading.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(heading)
        # create widget
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.setFixedHeight(25)
        self.layout().addWidget(widget)
        # finish
        self.row_number += 1
        return layout

    def insert(self):
        raise NotImplementedError

    def keys(self):
        return self._objs.keys()

    def len(self):
        raise NotImplementedError

    def pop(self):
        raise NotImplementedError

    def remove(self):
        raise NotImplementedError

    def values(self):
        return self._objs.values()
