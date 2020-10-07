#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains interpolator widget implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import layouts, buttons, label, sliders, checkbox, lineedit

from tpRigToolkit.tools.interpolateit.core import consts


class InterpolatorWidget(base.BaseWidget, object):

    closeWidget = Signal(object)
    deleteWidget = Signal(object)
    INTERP_HEIGHT = 150

    def __init__(self, client, parent=None):

        self._model = InterpolatorWidgetModel()
        self._controller = InterpolatorWidgetController(client=client, model=self._model)
        self._animation = None

        super(InterpolatorWidget, self).__init__(parent=parent)

        self.refresh()
        self.enable_buttons(False)

    @property
    def model(self):
        return self._model

    def get_main_layout(self):
        return layouts.VerticalLayout(spacing=0, margins=(0, 0, 0, 0))

    def ui(self):
        super(InterpolatorWidget, self).ui()

        self.setFixedHeight(self.INTERP_HEIGHT)

        main_frame = base.BaseFrame(parent=self)
        main_frame.setFixedHeight(self.INTERP_HEIGHT)
        self.main_layout.addWidget(main_frame)

        main_widget = QWidget()
        main_widget.setLayout(layouts.VerticalLayout(spacing=5, margins=(5, 5, 5, 5)))
        main_widget.setFixedHeight(150)
        main_widget.setFixedWidth(400)
        graphics_scene = QGraphicsScene()
        graphics_view = QGraphicsView()
        graphics_view.setScene(graphics_scene)
        graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        graphics_view.setFocusPolicy(Qt.NoFocus)
        graphics_view.setStyleSheet('QGraphicsView {border-style: none;}')
        graphics_view.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        main_frame.main_layout.addWidget(graphics_view)
        self._main_widget_proxy = graphics_scene.addWidget(main_widget)
        main_widget.setParent(graphics_view)

        title_layout = layouts.HorizontalLayout()
        select_layout = layouts.HorizontalLayout()
        button_layout = layouts.HorizontalLayout()
        slider_layout = layouts.HorizontalLayout()
        check_layout = layouts.HorizontalLayout()

        self._title_line = lineedit.BaseLineEdit(parent=self)
        self._close_btn = buttons.CloseButton('X', parent=self)
        title_layout.addWidget(self._title_line)
        title_layout.addWidget(self._close_btn)

        self._store_items_btn = buttons.BaseButton('Store Items', parent=self)
        self._clear_items_btn = buttons.BaseButton('Clear Items', parent=self)
        select_layout.addStretch()
        select_layout.addWidget(self._store_items_btn)
        select_layout.addWidget(self._clear_items_btn)
        select_layout.addStretch()

        self._store_start_btn = buttons.BaseButton('Store Start', parent=self)
        self._reset_item_btn = buttons.BaseButton('Reset', parent=self)
        self._store_end_btn = buttons.BaseButton('Store End', parent=self)
        button_layout.addWidget(self._store_start_btn)
        button_layout.addWidget(self._reset_item_btn)
        button_layout.addWidget(self._store_end_btn)

        self._start_label = label.BaseLabel('Start', parent=self)
        self._slider = sliders.BaseSlider(parent=self)
        self._slider.setRange(0, 49)
        self._slider.setOrientation(Qt.Horizontal)
        self._end_label = label.BaseLabel('End', parent=self)
        slider_layout.addWidget(self._start_label)
        slider_layout.addWidget(self._slider)
        slider_layout.addWidget(self._end_label)

        self._transforms_cbx = checkbox.BaseCheckBox('Transform', parent=self)
        self._user_attributes_cbx = checkbox.BaseCheckBox('UD Attributes', parent=self)
        check_layout.addStretch()
        check_layout.addWidget(self._transforms_cbx)
        check_layout.addWidget(self._user_attributes_cbx)
        check_layout.addStretch()

        main_widget.layout().addLayout(title_layout)
        main_widget.layout().addLayout(select_layout)
        main_widget.layout().addLayout(button_layout)
        main_widget.layout().addLayout(slider_layout)
        main_widget.layout().addLayout(check_layout)

    def setup_signals(self):
        self._slider.valueChanged.connect(self._controller.change_interpolate_value)
        self._slider.sliderReleased.connect(self._controller.end_slider_undo)
        self._transforms_cbx.toggled.connect(self._controller.change_transform_check)
        self._user_attributes_cbx.toggled.connect(self._controller.change_user_attributes_check)
        self._title_line.textChanged.connect(self._controller.change_title)
        self._store_items_btn.clicked.connect(self._controller.store_items)
        self._clear_items_btn.clicked.connect(self._controller.clear_items)
        self._store_start_btn.clicked.connect(self._controller.store_start_state)
        self._reset_item_btn.clicked.connect(self._controller.reset_attributes)
        self._store_end_btn.clicked.connect(self._controller.store_end_state)
        self._close_btn.clicked.connect(self._on_close_widget)

        self._model.itemsChanged.connect(self._on_items_changed)
        self._model.interpolateValueChanged.connect(self._on_interpolate_value_changed)
        self._model.transformCheckChanged.connect(self._transforms_cbx.setChecked)
        self._model.userAttributesCheckChanged.connect(self._user_attributes_cbx.setChecked)
        self._model.titleChanged.connect(self._title_line.setText)

    def refresh(self):
        self._slider.setValue(self._model.interpolate_value)
        self._transforms_cbx.setChecked(self._model.transform_check)
        self._user_attributes_cbx.setChecked(self._model.user_attributes_check)
        self._title_line.setText(self._model.title)

    def enable_buttons(self, flag):
        self._store_start_btn.setEnabled(flag)
        self._reset_item_btn.setEnabled(flag)
        self._store_end_btn.setEnabled(flag)
        self._transforms_cbx.setEnabled(flag)
        self._user_attributes_cbx.setEnabled(flag)
        self._start_label.setEnabled(flag)
        self._slider.setEnabled(flag)
        self._end_label.setEnabled(flag)

    def close_button_visible(self, flag):
        self._close_btn.setVisible(flag)

    def _on_items_changed(self, items):
        self.enable_buttons(bool(items))

    def animate_expand(self, value):

        size_animation = QPropertyAnimation(self, b'geometry')
        geometry = self.geometry()
        width = geometry.width()
        x, y, _, _ = geometry.getCoords()
        size_start = QRect(x, y, width, int(not value) * self.INTERP_HEIGHT)
        size_end = QRect(x, y, width, value * 150)
        size_animation.setStartValue(size_start)
        size_animation.setEndValue(size_end)
        size_animation.setDuration(200)
        size_anim_curve = QEasingCurve()
        size_anim_curve.setType(QEasingCurve.InQuad) if value else size_anim_curve.setType(QEasingCurve.OutQuad)
        size_animation.setEasingCurve(size_anim_curve)

        opacity_animation = QPropertyAnimation(self._main_widget_proxy, b'opacity')
        opacity_animation.setStartValue(not(value))
        opacity_animation.setEndValue(value)
        opacity_animation.setDuration(100)
        opacity_anim_curve = QEasingCurve()
        opacity_anim_curve.setType(QEasingCurve.InQuad) if value else opacity_anim_curve.setType(QEasingCurve.OutQuad)
        opacity_animation.setEasingCurve(opacity_anim_curve)

        # We must store the animation objects as a member variables. Otherwise the animation object could be deleted
        # once the function is completed. In that case, the animation will not work.
        self._animation = QSequentialAnimationGroup()
        if value:
            self._main_widget_proxy.setOpacity(0)
            self._animation.addAnimation(size_animation)
            self._animation.addAnimation(opacity_animation)
        else:
            self._main_widget_proxy.setOpacity(1)
            self._animation.addAnimation(opacity_animation)
            self._animation.addAnimation(size_animation)

        # When animating geometry property, the parent layout is not updated automatically.
        # We force the resize of the layout by calling a signal each time the size animation value changes.
        size_animation.valueChanged.connect(self._on_force_resize)
        self._animation.finished.connect(self._animation.clear)

        if not value:
            self._animation.finished.connect(self._on_delete_widget)

        self._animation.start(QAbstractAnimation.DeleteWhenStopped)

    def clear_animation(self):
        self._animation = None

    def _on_interpolate_value_changed(self, value):
        self._slider.blockSignals(True)
        self._slider.setValue(value)
        self._slider.blockSignals(False)

    def _on_force_resize(self, new_height):
        """
        Internal function that forces the resize of the parent layout of the widget
        We use the setFixedWidth function ot he widget to force its parent to reevaluate
        """

        self.setFixedHeight(new_height.height())

    def _on_close_widget(self):
        self.closeWidget.emit(self)

    def _on_delete_widget(self):
        self.deleteWidget.emit(self)


class InterpolatorWidgetModel(QObject, object):

    itemsChanged = Signal(dict)
    interpolateValueChanged = Signal(int)
    transformCheckChanged = Signal(bool)
    userAttributesCheckChanged = Signal(bool)
    sliderDownChanged = Signal(bool)
    titleChanged = Signal(str)

    def __init__(self):
        super(InterpolatorWidgetModel, self).__init__()

        self._items = dict()
        self._interpolate_value = 0
        self._transform_check = True
        self._user_attributes_check = False
        self._slider_down = False
        self._title = 'Untitled'

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, items_dict):
        self._items = items_dict
        self.itemsChanged.emit(items_dict)

    @property
    def interpolate_value(self):
        return self._interpolate_value

    @interpolate_value.setter
    def interpolate_value(self, value):
        self._interpolate_value = int(value)
        self.interpolateValueChanged.emit(self._interpolate_value)

    @property
    def transform_check(self):
        return self._transform_check

    @transform_check.setter
    def transform_check(self, flag):
        self._transform_check = bool(flag)
        self.transformCheckChanged.emit(self._transform_check)

    @property
    def user_attributes_check(self):
        return self._user_attributes_check

    @user_attributes_check.setter
    def user_attributes_check(self, flag):
        self._user_attributes_check = bool(flag)
        self.userAttributesCheckChanged.emit(self._user_attributes_check)

    @property
    def slider_down(self):
        return self._slider_down

    @slider_down.setter
    def slider_down(self, flag):
        self._slider_down = bool(flag)
        self.sliderDownChanged.emit(self._slider_down)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = str(value)
        self.titleChanged.emit(self._title)


class InterpolatorWidgetController(object):
    def __init__(self, client, model):
        super(InterpolatorWidgetController, self).__init__()

        self._client = client
        self._model = model

    @property
    def client(self):
        return self._client

    @property
    def model(self):
        return self._model

    def change_interpolate_value(self, value):
        self._model.interpolate_value = value
        self.set_linear_interpolation(value)

    def change_transform_check(self, flag):
        self._model.transform_check = flag

    def change_user_attributes_check(self, flag):
        self._model.user_attributes_check = flag

    def change_title(self, value):
        self._model.title = value

    def store_items(self):
        selection = self._client.selected_nodes()
        if not selection:
            return False

        self.clear_items()
        node_data = dict()
        for node in selection:
            node_data[node] = {
                consts.NODE_KEY: node, consts.START_KEY: dict(), consts.END_KEY: dict(), consts.CACHE_KEY: {}
            }

        self._model.items = node_data

    def clear_items(self):
        self._model.items = dict()

    def store_start_state(self):
        if not self._model.items:
            return

        self._store(consts.START_KEY, 0)
        self._cache()

    def store_end_state(self):
        if not self._model.items:
            return

        self._store(consts.END_KEY, 50)
        self._cache()

    def set_linear_interpolation(self, value):
        if not self._model.items:
            return

        if not self._model.slider_down:
            self._start_slider_undo()
            self._model.slider_down = True

        for item_dict in list(self._model.items.values()):
            node = item_dict[consts.NODE_KEY]
            start = item_dict[consts.START_KEY]
            if not start or not item_dict[consts.END_KEY]:
                continue
            cache = item_dict[consts.CACHE_KEY]
            for attr in list(cache.keys()):
                if cache[attr] is None:
                    continue
                self._client.set_stored_attribute_value(node, attr, cache[attr][value])

    def reset_attributes(self):
        if not self._model.items:
            return

        for item_dict in list(self._model.items.values()):
            node = item_dict[consts.NODE_KEY]
            attrs_data = self._client.get_attributes_data_to_store(
                node=node, transform_attributes=True, user_attributes=True)
            self._client.reset_attributes(node=node, attributes_dict=attrs_data)

    def _store(self, key, value):
        if not self._model.items:
            return

        for item_dict in list(self._model.items.values()):
            node = item_dict[consts.NODE_KEY]
            data = item_dict[key]
            attrs_data = self._client.get_attributes_data_to_store(
                node=node, transform_attributes=self._model.transform_check,
                user_attributes=self._model.user_attributes_check)
            for attr_name, attr_value in attrs_data.items():
                data[attr_name] = attr_value

        self._model.interpolate_value = value

    def _cache(self):
        for item_dict in list(self._model.items.values()):
            start = item_dict[consts.START_KEY]
            end = item_dict[consts.END_KEY]
            if not start or not end:
                item_dict[consts.CACHE_KEY] = None
                continue
            cache = item_dict[consts.CACHE_KEY] = dict()

            attrs = list(set(list(start.keys()) and set(list(end.keys()))))
            for attr in attrs:
                start_attr = start[attr]
                end_attr = end[attr]
                if start_attr == end_attr:
                    cache[attr] = None
                else:
                    cache_values = cache[attr] = list()
                    interval = float(end_attr - start_attr) / 49.0
                    for index in range(50):
                        cache_values.append((interval * index) + start_attr)

    def _start_slider_undo(self):
        self._client.enable_undo()

    def end_slider_undo(self):
        self._client.disable_undo()
        self._model.slider_down = False
