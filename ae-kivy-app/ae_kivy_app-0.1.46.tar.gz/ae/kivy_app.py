"""
main application classes and widgets for GUIApp-conform Kivy apps
=================================================================

This ae portion is providing two application classes (:class:`FrameworkApp` and :class:`KivyMainApp`),
various widget classes and some useful constants.


kivy app classes
----------------

The class :class:`KivyMainApp` is implementing a main app class that is reducing the amount of code needed for
to create a Python application based on the `kivy framework <https://kivy.org>`_.

:class:`KivyMainApp` is based on the following classes:

* the abstract base class :class:`~ae.gui_app.MainAppBase` which adds the concepts of :ref:`application status`
  (including :ref:`app-state-variables` and :ref:`app-state-constants`), :ref:`application flow` and
  :ref:`application events`.
* the class :class:`~ae.console.ConsoleApp` is adding :ref:`config-files`, :ref:`config-variables`
  and :ref:`config-options`.
* the class :class:`~ae.core.AppBase` is adding :ref:`application logging` and :ref:`application debugging`.

This namespace portion is also encapsulating the :class:`Kivy App class <kivy.app.App>` within the :class:`FrameworkApp`
class. This Kivy app class instance can be directly accessed from the main app class instance via the
:attr:`~ae.gui_app.MainAppBase.framework_app` attribute.


kivy widget classes
-------------------

* :class:`AppStateSlider`: :class:`~kivy.uix.slider.Slider>` changing the value of :ref:`app-state-variables`.
* :class:`FlowButton`: :class:`ImageButton` for to change the application flow.
* :class:`FlowDropDown`: :class:`~kivy.uix.dropdown.DropDown` for to process application flow.
* :class:`FlowInput`: dynamic kivy widget based on :class:`~kivy.uix.textinput.TextInput` with application flow support.
* :class:`FlowPopup`: :class:`~kivy.uix.popup.Popup` for to process application flow.
* :class:`FlowToggler`: toggle button based on :class:`ImageLabel` and :class:`~kivy.uix.behaviors.ToggleButtonBehavior`
  for to change the application flow.
* :class:`ImageLabel`: dynamic kivy widget extending the Kivy :class:`~kivy.uix.label.Label` widget with an image.
* :class:`ImageButton`: button widget based on :class:`~kivy.uix.behaviors.ButtonBehavior` with an additional image.
* :class:`MessageShowPopup`: simple message box widget.
* :class:`OptionalButton`: dynamic kivy widget based on :class:`FlowButton` which can be dynamically hidden.


text input widget
^^^^^^^^^^^^^^^^^

Until version 0.1.43 of this portion the background and text color switched with the light_theme app state.
Now all colors left unchanged (before only the ones with <unchanged>):

* background_color: Window.clearcolor            # default: 1, 1, 1, 1
* cursor_color: app.font_color                   # default: 1, 0, 0, 1
* disabled_foreground_color: <unchanged>         # default: 0, 0, 0, .5
* foreground_color: app.font_color               # default: 0, 0, 0, 1
* hint_text_color: <unchanged>                   # default: 0.5, 0.5, 0.5, 1.0
* selection_color: <unchanged>                   # default: 0.1843, 0.6549, 0.8313, .5

For to implement a nice dark background for the dark theme we would need also to change the images in the properties:
background_active, background_disabled_normal and self.background_normal.

TODO: replace/extend TextInputCutCopyPaste bubble widget of kivy.uix.textinput.TextInput with (1) theme colors and
(2) additional buttons for to add(Ctrl+Insert)/delete(Ctrl+Delete) autocompletion text entry (for mobile platforms).
Very ugly, but when FlowBubble gets implemented (inherited from kivy.uix.bubble.Bubble) then we could patch
kivy.uix.textinput.TextInputCutCopyPaste like::

    class TextInputCutCopyPaste(FlowBubble):
        ...

    from kivy.uix import textinput
    textinput.TextInputCutCopyPaste = TextInputCutCopyPaste
    from kivy.uix.textinput import TextInput


unit tests
----------

unit tests need at least V 2.0 of OpenGL and the kivy framework installed.

.. note::
    unit tests does have 100 % coverage but are currently not passing the gitlab CI tests because we failing in setup
    a proper running window system on the python image that all ae portions are using.

Any help for to fix the problems with the used gitlab CI image would be highly appreciated.
"""
import os
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

from plyer import vibrator                                                                  # type: ignore

import kivy                                                                                 # type: ignore
from kivy.animation import Animation                                                        # type: ignore
from kivy.app import App                                                                    # type: ignore
from kivy.clock import Clock                                                                # type: ignore
from kivy.core.audio import SoundLoader                                                     # type: ignore
from kivy.core.window import Window                                                         # type: ignore
from kivy.factory import Factory, FactoryException                                          # type: ignore
from kivy.input import MotionEvent                                                          # type: ignore
from kivy.lang import Builder, Observable, global_idmap                                     # type: ignore
from kivy.metrics import sp                                                                 # type: ignore
# pylint: disable=no-name-in-module
from kivy.properties import (                                                               # type: ignore
    BooleanProperty, DictProperty, ListProperty, ObjectProperty, StringProperty)
from kivy.uix.behaviors import ButtonBehavior, ToggleButtonBehavior                         # type: ignore
from kivy.uix.dropdown import DropDown                                                      # type: ignore
from kivy.uix.popup import Popup                                                            # type: ignore
from kivy.uix.slider import Slider                                                          # type: ignore
from kivy.uix.textinput import TextInput                                                    # type: ignore
from kivy.uix.widget import Widget                                                          # type: ignore

from ae.base import sys_platform                                                            # type: ignore
from ae.paths import app_docs_path                                                          # type: ignore
from ae.files import FilesRegister, CachedFile                                              # type: ignore
from ae.i18n import default_language, get_f_string, get_text                                # type: ignore
from ae.core import DEBUG_LEVEL_DISABLED, DEBUG_LEVEL_ENABLED                               # type: ignore

# id_of_flow not used here - added for easier import in app project
from ae.gui_app import (                                                                    # type: ignore
    AppStateType, APP_STATE_SECTION_NAME,
    THEME_LIGHT_BACKGROUND_COLOR, THEME_LIGHT_FONT_COLOR, THEME_DARK_BACKGROUND_COLOR, THEME_DARK_FONT_COLOR,
    id_of_flow, replace_flow_action
)
from ae.gui_help import layout_ps_hints, HelpAppBase                                        # type: ignore
from ae.kivy_auto_width import ContainerChildrenAutoWidthBehavior                           # type: ignore
from ae.kivy_dyn_chi import DynamicChildrenBehavior                                         # type: ignore
from ae.kivy_help import HelpBehavior, HelpLayout, HelpToggler                              # type: ignore
from ae.kivy_relief_canvas import ReliefCanvas                                              # type: ignore


__version__ = '0.1.46'


kivy.require('2.0.0')
# 1.9.1 is needed for Window.softinput_mode 'below_target'
# 2.0.0 is needed for Animation Sequence (>= 2.0.0rc2) and ScrollView recursion (> 2.0.0rc3) bug fixes

# if the entry field is on top of the screen then it will be disappear with below_target mode
# and in the default mode ('') the keyboard will cover the entry field if it is in the lower part of the screen
# therefore commented out the following two code lines (and setting it now depending on the entry field y position)
# if Window:                                  # is None on gitlab ci
#    Window.softinput_mode = 'below_target'   # ensure android keyboard is not covering Popup/text input if at bottom

MAIN_KV_FILE_NAME = 'main.kv'   #: default file name of the main kv file

""" sine 3 x deeper repeating animation, used e.g. for to animate ae.kivy_help.HelpLayout
Kivy version 2.0 needed; Animation Sequence bugs fixed in kivy master with the PR #5926, merged 7-May-2020.
"""
ANI_SINE_DEEPER_REPEAT3 = \
    Animation(ani_value=0.99, t='in_out_sine', d=0.6) + Animation(ani_value=0.87, t='in_out_sine', d=0.9) + \
    Animation(ani_value=0.96, t='in_out_sine', d=1.5) + Animation(ani_value=0.81, t='in_out_sine', d=0.9) + \
    Animation(ani_value=0.90, t='in_out_sine', d=0.6) + Animation(ani_value=0.54, t='in_out_sine', d=0.3)
ANI_SINE_DEEPER_REPEAT3.repeat = True

LOVE_VIBRATE_PATTERN = (0.0, 0.12, 0.12, 0.21, 0.03, 0.12, 0.12, 0.12)
""" short/~1.2s vibrate pattern for fun/love notification. """

ERROR_VIBRATE_PATTERN = (0.0, 0.09, 0.09, 0.18, 0.18, 0.27, 0.18, 0.36, 0.27, 0.45)
""" long/~2s vibrate pattern for error notification. """

CRITICAL_VIBRATE_PATTERN = (0.00, 0.12, 0.12, 0.12, 0.12, 0.12,
                            0.12, 0.24, 0.12, 0.24, 0.12, 0.24,
                            0.12, 0.12, 0.12, 0.12, 0.12, 0.12)
""" very long/~2.4s vibrate pattern for critical error notification (sending SOS to the mobile world;) """


# helper widgets with integrated app flow and observers ensuring change of app states (e.g. theme and size)
Builder.load_string('''\
#: import Window kivy.core.window.Window

#: import flow_action ae.gui_app.flow_action
#: import flow_key ae.gui_app.flow_key
#: import flow_key_split ae.gui_app.flow_key_split
#: import id_of_flow ae.gui_app.id_of_flow
#: import replace_flow_action ae.gui_app.replace_flow_action

#: import relief_colors ae.kivy_relief_canvas.relief_colors

<AppStateSlider>:
    help_id: app.main_app.help_app_state_id(self.app_state_name)
    help_vars: dict(state_name=self.app_state_name, state_value=self.value, self=self)
    value: app.app_states.get(self.app_state_name, (self.min + self.max) / 2) if self.app_state_name else self.value
    on_value: app.main_app.change_app_state(self.app_state_name, args[1])
    size_hint_y: None
    height: int(app.main_app.font_size * 1.5)
    cursor_size: int(app.main_app.font_size * 1.5), int(app.main_app.font_size * 1.5)
    padding: int(min(app.main_app.font_size * 2.4, sp(18)))
    value_track: True
    value_track_color: app.font_color[:3] + (0.39, )
    canvas.before:
        Color:
            rgba: Window.clearcolor
        Rectangle:
            pos: self.pos
            size: self.size

<ImageLabel@ReliefCanvas+Label>:
    ellipse_fill_ink: 1.0, 1.0, 1.0, 0.0
    ellipse_fill_pos: ()
    ellipse_fill_size: ()
    default_pos: self.default_pos or self.pos
    default_size: self.default_size or self.size
    image_pos: ()
    image_size: ()
    square_fill_ink: 1.0, 1.0, 1.0, 0.0
    square_fill_pos: ()
    square_fill_size: ()
    source: themeLabelImage.source
    size_hint: 1, None
    size_hint_min_x: self.height
    height: int(app.app_states['font_size'] * 1.5)
    font_size: app.app_states['font_size']
    color: app.font_color
    canvas.before:
        Color:
            rgba: self.square_fill_ink
        Rectangle:
            pos: self.square_fill_pos or self.default_pos or self.pos
            size: self.square_fill_size or self.default_size or self.size
        Color:
            rgba: self.ellipse_fill_ink
        Ellipse:
            pos: self.ellipse_fill_pos or self.default_pos or self.pos
            size: self.ellipse_fill_size or self.default_size or self.size
    Image:
        id: themeLabelImage
        source: root.source
        allow_stretch: True
        keep_ratio: False
        opacity: 1 if self.source else 0
        pos: self.parent.image_pos or self.parent.default_pos or self.parent.pos
        size: self.parent.image_size or self.parent.default_size or self.parent.size

<FlowInput>:
    help_id: app.main_app.help_flow_id(self.focus_flow_id)
    help_vars: dict(new_flow_id=self.focus_flow_id, self=self)
    font_size: app.app_states['font_size']
    multiline: False
    write_tab: False
    use_bubble: True
    use_handles: True

<FlowButton>:
    help_id: app.main_app.help_flow_id(self.tap_flow_id)
    help_vars: dict(new_flow_id=self.tap_flow_id, self=self)
    icon_name: ""
    on_release: app.main_app.change_flow(self.tap_flow_id, **self.tap_kwargs)
    source:
        app.main_app.img_file(self.icon_name or flow_key_split(self.tap_flow_id)[0], \
                              app.app_states['font_size'], app.app_states['light_theme'])

<OptionalButton@FlowButton>:
    visible: False
    size_hint: None, None
    height: int(app.app_states['font_size'] * 1.5) if self.visible else 0
    width: self.height if self.visible else 0
    disabled: not self.visible
    opacity: 1 if self.visible else 0

<FlowDropDown>:             # DropDown flow gets handled similar to a Popup
    close_kwargs:
        dict(flow_id=id_of_flow('', '')) if app.main_app.flow_path_action(path_index=-2) in ('', 'enter') else dict()
    on_dismiss: app.main_app.change_flow(id_of_flow('close', 'flow_popup'), **self.close_kwargs)
    auto_width: False
    # width determined by ContainerChildrenAutoWidthBehavior, so no need for: width: min(Window.width - sp(96), sp(960))
    canvas.before:
        Color:
            rgba: Window.clearcolor
        RoundedRectangle:
            pos: self.pos
            size: self.size
    canvas.after:
        Color:
            rgba: app.font_color
        Line:
            width: sp(1.8)
            rounded_rectangle: self.x, self.y, self.width, self.height, sp(9)

<FlowPopup>:
    close_kwargs:
        dict(flow_id=id_of_flow('', '')) if app.main_app.flow_path_action(path_index=-2) in ('', 'enter') else dict()
    on_dismiss: app.main_app.change_flow(id_of_flow('close', 'flow_popup'), **self.close_kwargs)
    title_color: app.font_color
    separator_color: app.font_color
    background: ""
    background_color: Window.clearcolor
    title_align: 'center'
    title_size: app.main_app.font_size
    canvas.before:
        Color:
            rgba: Window.clearcolor
        RoundedRectangle:
            pos: self.pos
            size: self.size

<FlowToggler>:
    tap_flow_id: ''
    help_id: app.main_app.help_flow_id(self.tap_flow_id)
    help_vars: dict(new_flow_id=self.tap_flow_id, self=self)
    icon_name: ""
    on_release: app.main_app.change_flow(self.tap_flow_id, **self.tap_kwargs)
    source:
        app.main_app.img_file(self.icon_name or flow_key_split(self.tap_flow_id)[0], \
                              app.app_states['font_size'], app.app_states['light_theme'])

<MessageShowPopup>:
    size_hint: 0.9, None
    height: int(min(Window.height - sp(96), self.children[0].minimum_height + msg_txt_box.height))
    ScrollView:
        Label:
            id: msg_txt_box
            text: root.message
            font_size: app.main_app.font_size
            text_size: self.width, None
            size_hint: 1, None
            height: self.texture_size[1]
            color: app.font_color
            Button:     # invisible button for to close popup on message text click
                pos: msg_txt_box.pos
                size: msg_txt_box.size
                background_color: 0, 0, 0, 0
                on_release: root.dismiss()
''')


def ensure_tap_kwargs_refs(init_kwargs: Dict[str, Any], tap_widget: Widget):
    """ ensure that the passed widget.__init__ kwargs dict contains a reference to itself within kwargs['tap_kwargs'].

    :param init_kwargs:         kwargs of the widgets __init__ method.
    :param tap_widget:          reference to the tap widget.

    This alternative version is only 10 % faster but much more confusing than the current implementation::

        if 'tap_kwargs' not in init_kwargs:
            init_kwargs['tap_kwargs'] = dict()
        tap_kwargs = init_kwargs['tap_kwargs']

        if 'tap_widget' not in tap_kwargs:
            tap_kwargs['tap_widget'] = tap_widget

        if 'popup_kwargs' not in tap_kwargs:
            tap_kwargs['popup_kwargs'] = dict()
        popup_kwargs = tap_kwargs['popup_kwargs']
        if 'parent' not in popup_kwargs:
            popup_kwargs['parent'] = tap_widget

    """
    init_kwargs['tap_kwargs'] = tap_kwargs = init_kwargs.get('tap_kwargs', dict())
    tap_kwargs['tap_widget'] = tap_kwargs.get('tap_widget', tap_widget)
    tap_kwargs['popup_kwargs'] = popup_kwargs = tap_kwargs.get('popup_kwargs', dict())
    popup_kwargs['parent'] = popup_kwargs.get('parent', tap_widget)


class AppStateSlider(HelpBehavior, Slider):
    """ slider widget with help text for to change app state value. """
    app_state_name = StringProperty()   #: name of the app state to be changed by this slider value


class ImageButton(ButtonBehavior, Factory.ImageLabel):                                               # pragma: no cover
    """ theme-able button base class with additional events for double/triple/long touches.

    :Events:
        `on_double_tap`:
            Fired with the touch down MotionEvent instance arg when a button get tapped twice within short time.
        `on_triple_tap`:
            Fired with the touch down MotionEvent instance arg when a button get tapped three times within short time.
        `on_long_tap`:
            Fired with the touch down MotionEvent instance arg when a button get tapped more than 2.4 seconds.
        `on_alt_tap`:
            Fired with the touch down MotionEvent instance arg when a button get either double, triple or long tapped.

    .. note::
        unit tests are still missing for this widget.

    """
    def __init__(self, **kwargs):
        # register before call of super().__init__() for to prevent errors, e.g. "AttributeError: long_tap"
        self.register_event_type('on_double_tap')   # pylint: disable=maybe-no-member
        self.register_event_type('on_triple_tap')   # pylint: disable=maybe-no-member
        self.register_event_type('on_long_tap')     # pylint: disable=maybe-no-member
        self.register_event_type('on_alt_tap')      # pylint: disable=maybe-no-member
        super().__init__(**kwargs)

    def on_touch_down(self, touch: MotionEvent) -> bool:
        """ check for additional events added by this class.

        :param touch:   motion/touch event data.
        :return:        True if event got processed/used.
        """
        if not self.disabled and self.collide_point(touch.x, touch.y):
            is_triple = touch.is_triple_tap
            if is_triple or touch.is_double_tap:
                # pylint: disable=maybe-no-member
                self.dispatch('on_triple_tap' if is_triple else 'on_double_tap', touch)
                self.dispatch('on_alt_tap', touch)
                return True
            # pylint: disable=maybe-no-member
            touch.ud['long_touch_handler'] = long_touch_handler = lambda dt: self.dispatch('on_long_tap', touch)
            Clock.schedule_once(long_touch_handler, 2.4)
        return super().on_touch_down(touch)         # does touch.grab(self)

    @staticmethod
    def _cancel_long_touch_clock(touch) -> bool:
        long_touch_handler = touch.ud.pop('long_touch_handler', None)
        if long_touch_handler:
            Clock.unschedule(long_touch_handler)    # alternatively: long_touch_handler.cancel()
        return bool(long_touch_handler)

    def on_touch_move(self, touch: MotionEvent) -> bool:
        """ disable long touch on mouse/finger moves.

        :param touch:   motion/touch event data.
        :return:        True if event got processed/used.
        """
        # alternative method to calculate touch.pos distances is (from tripletap.py):
        # Vector.distance(Vector(ref.sx, ref.sy), Vector(touch.osx, touch.osy)) > 0.009
        if abs(touch.ox - touch.x) > 9 and abs(touch.oy - touch.y) > 9 and self.collide_point(touch.x, touch.y):
            self._cancel_long_touch_clock(touch)
        return super().on_touch_move(touch)

    def on_touch_up(self, touch: MotionEvent) -> bool:
        """ disable long touch on mouse/finger up.

        :param touch:   motion/touch event data.
        :return:        True if event got processed/used.
        """
        if touch.grab_current is self:
            if not self._cancel_long_touch_clock(touch):
                touch.ungrab(self)
                return True     # prevent popup/dropdown dismiss
        return super().on_touch_up(touch)   # does touch.ungrab(self)

    def on_alt_tap(self, touch: MotionEvent):
        """ default handler for alternative tap (double, triple or long tap/click).

        :param touch:   motion/touch event data with the touched widget in `touch.grab_current`.
        """

    def on_double_tap(self, touch: MotionEvent):
        """ double tap/click default handler.

        :param touch:   motion/touch event data with the touched widget in `touch.grab_current`.
        """

    def on_triple_tap(self, touch: MotionEvent):
        """ triple tap/click default handler.

        :param touch:   motion/touch event data with the touched widget in `touch.grab_current`.
        """

    def on_long_tap(self, touch: MotionEvent):
        """ long tap/click default handler.

        :param touch:   motion/touch event data with the touched widget in `touch.grab_current`.
        """
        # for to prevent dismiss via super().on_touch_up: exclusive receive of this touch up event in self.on_touch_up
        touch.grab(self, exclusive=True)

        # remove 'long_touch_handler' key from touch.ud dict although just fired for to signalize that
        # the long tap event got handled in self.on_touch_up (for to return True)
        self._cancel_long_touch_clock(touch)

        # also dispatch as alternative tap
        self.dispatch('on_alt_tap', touch)


class FlowButton(HelpBehavior, ImageButton):                                            # pragma: no cover
    """ has to be declared after the declaration of the ImageButton widget class """
    tap_flow_id = StringProperty()  #: the new flow id that will be set when this button get tapped
    tap_kwargs = ObjectProperty()   #: kwargs dict passed to event handler (change_flow) when button get tapped

    def __init__(self, **kwargs):
        ensure_tap_kwargs_refs(kwargs, self)
        super().__init__(**kwargs)


class FlowDropDown(ContainerChildrenAutoWidthBehavior, DynamicChildrenBehavior, ReliefCanvas,
                   DropDown):                                                                         # pragma: no cover
    """ drop down widget used for user selections from a list of items (represented by the children-widgets). """
    close_kwargs = DictProperty()               #: kwargs passed to all close action flow change event handlers
    parent_popup_to_close = ObjectProperty()    #: tuple of popup widget instances to be closed if this drop down closes

    def dismiss(self, *args):
        """ override DropDown method for to prevent dismiss of any dropdown/popup while clicking on activator widget.

        :param args:        args to be passed to DropDown.dismiss().
        """
        app = App.get_running_app()
        if app.help_layout is None or not isinstance(app.help_layout.target, HelpToggler):
            super().dismiss(*args)

    def on_touch_down(self, touch: MotionEvent) -> bool:
        """ prevent the processing of a touch on the help activator widget by this drop down.

        :param touch:   motion/touch event data.
        :return:        True if event got processed/used.
        """
        if App.get_running_app().main_app.help_activator.collide_point(*touch.pos):
            return False        # allow help activator button to process this touch down event
        return super().on_touch_down(touch)


class FlowInput(HelpBehavior, TextInput):                                                             # pragma: no cover
    """ text input/edit widget with optional autocompletion. """
    focus_flow_id = StringProperty()        #: flow id that will be set when this widget get focus
    unfocus_flow_id = StringProperty()      #: flow id that will be set when this widget get focus

    auto_complete_texts: List[str] = ListProperty()     #: list of autocompletion texts
    auto_complete_selector_index_ink: Tuple[float, float, float, float] = ListProperty((0.69, 0.69, 0.69, 1))
    """ color and alpha used for to highlight the currently selected text of all matching autocompletion texts """

    _ac_dropdown: Any = None                            #: singleton FlowDropDown instance for all TextInput instances
    _matching_ac_texts: List[str] = list()              #: one list instance for all TextInput instances is enough
    _matching_ac_index: int = 0                         #: index of selected text in the drop down matching texts list

    def __init__(self, **kwargs):
        # changed to kivy properties so no need to pop them from kwargs:
        # self.auto_complete_texts = kwargs.pop('auto_complete_texts', list())
        # self.auto_complete_selector_index_ink = kwargs.pop('auto_complete_selector_index_ink', (0.69, 0.69, 0.69, 1))

        super().__init__(**kwargs)

        if not FlowInput._ac_dropdown:
            FlowInput._ac_dropdown = FlowDropDown()     # widget instances cannot be created in class var declaration

    def _change_selector_index(self, delta: int):
        """ change/update/set the index of the matching texts in the opened autocompletion dropdown.

        :param delta:           index delta value between old and new index (e.g. pass +1 to increment index).
                                Set index to zero if the old/last index was on the last item in the matching list.
        """
        cnt = len(self._matching_ac_texts)
        chi = list(reversed(self._ac_dropdown.container.children))
        idx = self._matching_ac_index
        chi[idx].square_fill_ink = Window.clearcolor
        self._matching_ac_index = (idx + delta + cnt) % cnt
        chi[self._matching_ac_index].square_fill_ink = self.auto_complete_selector_index_ink
        self.suggestion_text = self._matching_ac_texts[self._matching_ac_index][len(self.text):]    # type: ignore #mypy

    def _delete_ac_text(self):
        ac_text = self._matching_ac_texts[self._matching_ac_index]
        self.auto_complete_texts.remove(ac_text)
        self.on_text(self, self.text)       # redraw autocompletion dropdown

    def _extend_ac_texts(self):
        self.auto_complete_texts.insert(0, self.text)

    def keyboard_on_key_down(self, window: Any, keycode: Tuple[int, str], text: str, modifiers: List[str]) -> bool:
        """ overwritten TextInput/FocusBehavior kbd event handler.

        :param window:          keyboard window.
        :param keycode:         pressed key as tuple of (numeric key code, key name string).
        :param text:            pressed key value string.
        :param modifiers:       list of modifier keys (pressed or locked).
        :return:                True if key event get processed/used by this method.
        """
        key_name = keycode[1]
        if self._ac_dropdown.attach_to:
            if key_name in ('enter', 'right'):
                self.suggestion_text = ""
                self.text = self._matching_ac_texts[self._matching_ac_index]
                self._ac_dropdown.dismiss()
                return True

            if key_name == 'down':
                self._change_selector_index(1)
            elif key_name == 'up':
                self._change_selector_index(-1)
            elif key_name == 'delete' and 'ctrl' in modifiers:
                self._delete_ac_text()

        if key_name == 'insert' and 'ctrl' in modifiers:
            self._extend_ac_texts()

        return super().keyboard_on_key_down(window, keycode, text, modifiers)

    def on_focus(self, _self, focus: bool):
        """ change flow on text input change of focus.

        :param _self:
        :param focus:           True if this text input got focus, False on unfocus.
        """
        if focus:
            flow_id = self.focus_flow_id or id_of_flow('edit')
        else:
            flow_id = self.unfocus_flow_id or id_of_flow('close')
        App.get_running_app().main_app.change_flow(flow_id)

    def on_text(self, _self, text: str):
        """ TextInput.text change event handler.

        :param _self:           unneeded duplicate reference to TextInput/self.
        :param text:            new/current text property value.
        """
        if text:
            matching = [txt for txt in self.auto_complete_texts if txt[:-1].startswith(text)]
        else:
            matching = list()
        self._matching_ac_texts[:] = matching
        self._matching_ac_index = 0

        if matching:
            cdm = list()
            for txt in matching:
                cdm.append(dict(cls='FlowButton', kwargs=dict(text=txt, on_release=self._select_ac_text)))
            self._ac_dropdown.child_data_maps[:] = cdm
            if not self._ac_dropdown.attach_to:
                App.get_running_app().main_app.change_flow(replace_flow_action(self.focus_flow_id, 'suggest'))
                self._ac_dropdown.open(self)
            self._change_selector_index(0)
            self.suggestion_text = matching[self._matching_ac_index][len(self.text):]
        elif self._ac_dropdown.attach_to:
            self._ac_dropdown.dismiss()

    def _select_ac_text(self, selector: Widget):
        """ put selected autocompletion text into text input and close _ac_dropdown """
        self.text = selector.text
        self._ac_dropdown.dismiss()


class FlowPopup(ContainerChildrenAutoWidthBehavior, DynamicChildrenBehavior, ReliefCanvas, Popup):    # pragma: no cover
    """ pop up widget used for dialogs and other top-most or modal windows. """
    close_kwargs = DictProperty()               #: kwargs passed to all close action flow change event handlers
    parent_popup_to_close = ObjectProperty()    #: tuple of popup widget instances to be closed if this popup closes

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_key_down=self.on_key_down)

    def dismiss(self, *args, **kwargs):
        """ override ModalView method for to prevent dismiss of any dropdown/popup while clicking on activator widget.

        :param args:        args to be passed to ModalView.dismiss().
        :param kwargs:      kwargs to be passed to ModalView.dismiss().
        """
        app = App.get_running_app()
        if app.get_running_app().help_layout is None or not isinstance(app.help_layout.target, HelpToggler):
            super().dismiss(*args, **kwargs)

    def on_key_down(self, _instance, key, _scancode, _codepoint, _modifiers):
        """ close/dismiss this popup if back/Esc key get pressed - allowing stacking with DropDown/FlowDropDown. """
        if key == 27 and self.get_parent_window():
            self.dismiss()
            return True
        return False

    def on_touch_down(self, touch: MotionEvent) -> bool:
        """ prevent the processing of a touch on the help activator widget by this popup.

        :param touch:   motion/touch event data.
        :return:        True if event got processed/used.
        """
        if App.get_running_app().main_app.help_activator.collide_point(*touch.pos):
            return False        # allow help activator button to process this touch down event
        return super().on_touch_down(touch)


class FlowToggler(HelpBehavior, ToggleButtonBehavior, Factory.ImageLabel):                          # pragma: no cover
    """ toggle button changing flow id. """
    tap_flow_id = StringProperty()          #: the new flow id that will be set when this toggle button get released
    tap_kwargs = DictProperty()             #: kwargs dict passed to event handler (change_flow) when button get tapped

    def __init__(self, **kwargs):
        ensure_tap_kwargs_refs(kwargs, self)
        super().__init__(**kwargs)


class FrameworkApp(App):
    """ kivy framework app class proxy redirecting events and callbacks to the main app class instance. """

    app_states = DictProperty()                             #: duplicate of MainAppBase app state for events/binds
    displayed_help_id = StringProperty()                    #: help id of the currently explained/help-target widget
    help_layout = ObjectProperty(allownone=True)            #: layout widget if help mode is active else None

    landscape = BooleanProperty()                           #: True if app win width is bigger than the app win height
    font_color = ObjectProperty(THEME_DARK_FONT_COLOR)      #: rgba color of the font used for labels/buttons/...
    mixed_back_ink = ListProperty((.69, .69, .69, 1.))      #: background color mixed from available back inks

    def __init__(self, main_app: 'KivyMainApp', **kwargs):
        """ init kivy app """
        self.main_app = main_app                            #: set reference to KivyMainApp instance
        self.title = main_app.app_title                     #: set kivy.app.App.title
        self.icon = os.path.join("img", "app_icon.png")     #: set kivy.app.App.icon

        super().__init__(**kwargs)

        # redirecting class name, app name and directory to the main app class for kv/ini file names is
        # .. no longer needed because main.kv get set in :meth:`KivyMainApp.init_app` and app states
        # .. get stored in the :ref:`ae config files <config-files>`.
        # self.__class__.__name__ = main_app.__class__.__name__
        # self._app_name = main_app.app_name
        # self._app_directory = '.'

    def build(self) -> Widget:
        """ kivy build app callback.

        :return:                root widget (Main instance) of this app.
        """
        Window.bind(on_resize=self.win_pos_size_change,
                    left=self.win_pos_size_change,
                    top=self.win_pos_size_change,
                    on_key_down=self.key_press_from_kivy,
                    on_key_up=self.key_release_from_kivy)

        self.main_app.framework_root = root = Factory.Main()
        return root

    def key_press_from_kivy(self, keyboard: Any, key_code: int, _scan_code: int, key_text: Optional[str],
                            modifiers: List[str]) -> bool:
        """ convert and redistribute key down/press events coming from Window.on_key_down.

        :param keyboard:        used keyboard.
        :param key_code:        key code of pressed key.
        :param _scan_code:      key scan code of pressed key.
        :param key_text:        key text of pressed key.
        :param modifiers:       list of modifier keys (including e.g. 'capslock', 'numlock', ...)
        :return:                True if key event got processed used by the app, else False.
        """
        return self.main_app.key_press_from_framework(
            "".join(_.capitalize() for _ in sorted(modifiers) if _ in ('alt', 'ctrl', 'meta', 'shift')),
            keyboard.command_keys.get(key_code) or key_text or str(key_code))

    def key_release_from_kivy(self, keyboard, key_code, _scan_code) -> bool:
        """ key release/up event.

        :return:                return value of call to `on_key_release` (True if ke got processed/used).
        """
        return self.main_app.call_method('on_key_release', keyboard.command_keys.get(key_code, str(key_code)))

    def on_start(self):
        """ kivy app start event, called after :meth:`MainAppBase.run_app` method and MainAppBase.on_app_start event.

        Kivy just created the main layout by calling its :meth:`~kivy.app.App.build` method and
        attached it to the main window.

        Emits the `on_kivy_app_start` event.
       """
        self.main_app.framework_win = self.root.parent
        self.win_pos_size_change()  # init. app./self.landscape (on app startup and after build)
        self.main_app.call_method('on_kivy_app_start')

    def on_pause(self) -> bool:
        """ app pause event automatically saving the app states.

        Emits the `on_app_pause` event.

        :return:                True.
        """
        self.main_app.save_app_states()
        self.main_app.call_method('on_app_pause')
        return True

    def on_resume(self) -> bool:
        """ app resume event automatically loading the app states.

        Emits the `on_app_resume` event.

        :return:                True.
        """
        self.main_app.load_app_states()
        self.main_app.call_method('on_app_resume')
        return True

    def on_stop(self):
        """ quit app event automatically saving the app states.

        Emits the `on_kivy_app_stop` event whereas the method :meth:`~ae.gui_app.MainAppBase.stop_app`
        emits the `on_app_stop` event.
        """
        self.main_app.save_app_states()
        self.main_app.call_method('on_kivy_app_stop')

    def win_pos_size_change(self, *_):
        """ resize handler updates: :attr:`~ae.gui_app.MainAppBase.win_rectangle`, :attr:`~FrameworkApp.landscape`. """
        self.main_app.win_pos_size_change(Window.left, Window.top, Window.width, Window.height)


class MessageShowPopup(FlowPopup):
    """ flow popup for to display info or error messages. """
    title = StringProperty(get_text("Error"))       #: popup window title
    message = StringProperty()                      #: popup window label text (message to display)


class _GetTextBinder(Observable):
    """ redirect :func:`ae.i18n.get_f_string` to an instance of this class.

    kivy currently only support a single one automatic binding in kv files for all function names ending with `_`
    (see `watched_keys` extension in kivy/lang/parser.py line 201; e.g. `f_` would get recognized by the lang_tr
    re pattern, but kivy will only add the `_` symbol to watched_keys and therefore `f_` not gets bound.)
    For to allow both - f-strings and simple get_text messages - this module binds only :func:`ae.i18n.get_f_string`
    to the `get_txt` symbol (instead of :func:`ae.i18n.get_text` to `_` and :func:`ae.i18n.get_f_string` to `f_`).

    :data:`get_txt` can be used as translation callable, but also for to switch the current default language.
    Additionally :data:`get_txt` is implemented as an observer that automatically updates any translations
    messages of all active/visible kv rules on switch of the language at app run-time.

    inspired by (see also discussion at https://github.com/kivy/kivy/issues/1664):

    - https://github.com/tito/kivy-gettext-example
    - https://github.com/Kovak/kivy_i18n_test
    - https://git.bluedynamics.net/phil/woodmaster-trainer/-/blob/master/src/ui/kivy/i18n.py

    """
    observers: List[Tuple[Callable, tuple, dict]] = []
    _bound_uid = -1

    def fbind(self, name: str, func: Callable, *args, **kwargs) -> int:
        """ override fbind (fast bind) from :class:`Observable` for to collect and separate `_` bindings.

        :param name:            attribute name to be bound.
        :param func:            observer notification function (to be called if attribute changes).
        :param args:            args to be passed to the observer.
        :param kwargs:          kwargs to be passed to the observer.
        :return:                unique id of this binding.
        """
        if name == "_":
            # noinspection PyUnresolvedReferences
            self.observers.append((func.__call__, args, kwargs))    # type: ignore  # __call__ to prevent weakly-ref-err
            # Observable.bound_uid - initialized in _event.pyx/Observable.cinit() - is not available in python:
            # uid = self.bound_uid      # also not available via getattr(self, 'bound_uid')
            # self.bound_uid += 1
            # return uid
            uid = self._bound_uid
            self._bound_uid -= 1
            return uid                  # alternative ugly hack: return -len(self.observers)

        return super().fbind(name, func, *args, **kwargs)

    def funbind(self, name: str, func: Callable, *args, **kwargs):
        """ override fast unbind.

        :param name:            bound attribute name.
        :param func:            observer notification function (called if attribute changed).
        :param args:            args to be passed to the observer.
        :param kwargs:          kwargs to be passed to the observer.
        """
        if name == "_":
            # noinspection PyUnresolvedReferences
            key = (func.__call__, args, kwargs)         # type: ignore  # __call__ to prevent ReferenceError: weakly-ref
            if key in self.observers:
                self.observers.remove(key)
        else:
            super().funbind(name, func, *args, **kwargs)

    def switch_lang(self, lang_code: str):
        """ change language and update kv rules properties.

        :param lang_code:       language code to switch this app to.
        """
        default_language(lang_code)

        app = App.get_running_app()

        for func, args, _kwargs in self.observers:
            app.main_app.vpo(f"_GetTextBinder.switch_lang({lang_code}) calling observer {str(args[0])[:45]}")
            try:
                func(args[0], None, None)
            except ReferenceError as ex:  # pragma: no cover # ReferenceError: weakly-referenced object no longer exists
                app.main_app.dpo(f"_GetTextBinder.switch_lang({lang_code}) exception {ex}")

        app.title = get_txt(app.main_app.app_title)

    def __call__(self, text: str, count: Optional[int] = None, language: str = '',
                 loc_vars: Optional[Dict[str, Any]] = None, **kwargs) -> str:
        """ translate text into the current-default or the passed language.

        :param text:            text to translate.
        :param count:           optional count for pluralization.
        :param language:        language code to translate the passed text to (def=current default language).
        :param loc_vars:        local variables used in the conversion of the f-string expression to a string.
                                The `count` item of this dict will be overwritten by the value of the
                                :paramref:`~_GetTextBinder.__call__.count` parameter (if this argument got passed).
        :param kwargs:          extra kwargs (e.g. :paramref:`~ae.i18n.get_f_string.glo_vars` or
                                :paramref:`~ae.i18n.get_f_string.key_suffix` - see :func:`~ae.i18n.get_f_string`).
        :return:                translated text.
        """
        if count is not None:
            if loc_vars is None:
                loc_vars = dict()
            loc_vars['count'] = count
        return get_f_string(text, language=language, loc_vars=loc_vars, **kwargs)


# Sphinx make html fails if the comment underneath is included into autodoc/autosummary (by changing '# ' into '#: ')
get_txt = _GetTextBinder()      #: instantiate global i18n translation callable and language switcher
get_txt.__qualname__ = 'GetTextBinder'      # hide sphinx build warning (build crashes if get_txt get documented)
global_idmap['_'] = get_txt                 # bind as function/callable with the name `_` for to be used in kv files


class KivyMainApp(HelpAppBase):
    """ Kivy application """
    flow_id_ink: tuple = (0.99, 0.99, 0.69, 0.69)           #: rgba color for flow id / drag&drop node placeholder
    flow_path_ink: tuple = (0.99, 0.99, 0.39, 0.48)         #: rgba color for flow_path/drag&drop item placeholder
    selected_item_ink: tuple = (0.69, 1.0, 0.39, 0.18)      #: rgba color for list items (selected)
    unselected_item_ink: tuple = (0.39, 0.39, 0.39, 0.18)   #: rgba color for list items (unselected)

    get_txt_ = get_txt                                      #: make i18n translations available via main app instance
    kbd_input_mode: str = 'pan'                             #: optional app state for to set Window[Base].softinput_mode
    documents_root_path: str = "."                          #: root file path for app documents, e.g. for import/export

    _debug_enable_clicks: int = 0

    # abstract methods

    def init_app(self, framework_app_class: Type[FrameworkApp] = FrameworkApp
                 ) -> Tuple[Optional[Callable], Optional[Callable]]:
        """ initialize framework app instance and prepare app startup.

        :param framework_app_class:     class to create app instance (optionally extended by app project).
        :return:                        callable for to start and stop/exit the GUI event loop.
        """
        self.documents_root_path = app_docs_path()

        self.framework_app = framework_app_class(self)
        if os.path.exists(MAIN_KV_FILE_NAME):
            self.framework_app.kv_file = MAIN_KV_FILE_NAME

        return self.framework_app.run, self.framework_app.stop

    # overwritten and helper methods

    def change_light_theme(self, light_theme: bool):
        """ change font and window clear/background colors to match 'light'/'black' themes.

        :param light_theme:     pass True for light theme, False for black theme.
        """
        Window.clearcolor = THEME_LIGHT_BACKGROUND_COLOR if light_theme else THEME_DARK_BACKGROUND_COLOR
        self.framework_app.font_color = THEME_LIGHT_FONT_COLOR if light_theme else THEME_DARK_FONT_COLOR

    @staticmethod
    def class_by_name(class_name: str) -> Optional[Type]:
        """ resolve kv widgets """
        try:
            return Factory.get(class_name)
        except (FactoryException, AttributeError):
            return None

    def ensure_top_most_z_index(self, widget: Any):
        """ ensure visibility of the passed widget to be the top most in the z index/order

        :param widget:          widget to check and possibly correct to be the top most one.
        """
        if self.framework_win.children[0] != widget:            # if other dropdown/popup opened after help layout
            self.framework_win.remove_widget(widget)            # then correct z index/order to show help text in front
            self.framework_win.add_widget(widget)

    def help_activation_toggle(self):                                               # pragma: no cover
        """ button tapped event handler for to switch help mode between active and inactive.
        """
        activator = self.help_activator
        activate = self.help_layout is None
        hlw = None
        if activate:
            hlw = HelpLayout(target=activator,
                             ps_hints=layout_ps_hints(*activator.to_window(*activator.pos), *activator.size,
                                                      self.framework_win.width, self.framework_win.height))
            self.framework_win.add_widget(hlw)
        else:
            ANI_SINE_DEEPER_REPEAT3.stop(self.help_layout)
            ANI_SINE_DEEPER_REPEAT3.stop(activator)
            self.framework_win.remove_widget(self.help_layout)

        self.change_observable('help_layout', hlw)

        if hlw:
            self.help_display('', dict())           # show initial help text (after self.help_layout got set)
            ANI_SINE_DEEPER_REPEAT3.start(hlw)
            ANI_SINE_DEEPER_REPEAT3.start(activator)

    def on_help_displayed(self):                                                    # pragma: no cover
        """ start timer for automatic reset or disable of the help mode.

        The first plan to animate :attr:`~HelpAppBase.help_layout` widget instead of target to drift back
        to :attr:`~HelpAppBase.help_activator` would need to temporarily deactivate the layout_x/y/pos_hints.
        """
        hlw = self.help_layout
        hlw.cancel_ani_slide_back()

        if self.displayed_help_id:
            hlw.begin_ani_slide_back(self.help_activator.pos)

    def load_sounds(self):
        """ override for to pre-load audio sounds from app folder snd into sound file cache. """
        self.sound_files = FilesRegister('snd/**', file_class=CachedFile,
                                         object_loader=lambda f: SoundLoader.load(f.path))

    def mix_background_ink(self):
        """ remix background ink if one of the basic back colours change. """
        self.framework_app.mixed_back_ink = (sum(_) / len(_) for _ in zip(
            self.flow_id_ink, self.flow_path_ink, self.selected_item_ink, self.unselected_item_ink))

    def on_app_init(self):
        """ setup loaded app states within the now available framework app and its widgets. """
        # redirect back ink app state color changes to actualize mixed_back_ink
        setattr(self, 'on_flow_id_ink', self.mix_background_ink)
        setattr(self, 'on_flow_path_ink', self.mix_background_ink)
        setattr(self, 'on_selected_item_ink', self.mix_background_ink)
        setattr(self, 'on_unselected_item_ink', self.mix_background_ink)

    def on_app_start(self):                                                                     # pragma: no cover
        """ app start event handler - used for to set the window pos and size. """
        # super().on_app_start()      # call of ae.gui_app.MainAppBase.on_app_start() not needed
        get_txt.switch_lang(self.lang_code)
        self.change_light_theme(self.light_theme)

        win_rect = self.win_rectangle
        if win_rect:                                # is empty tuple at very first app start
            Window.left, Window.top = win_rect[:2]
            Window.size = win_rect[2:]

    def on_flow_widget_focused(self):
        """ set focus to the widget referenced by the current flow id. """
        liw = self.widget_by_flow_id(self.flow_id)
        self.vpo(f"KivyMainApp.on_flow_widget_focused() '{self.flow_id}'"
                 f" {liw} has={getattr(liw, 'focus', 'unsupported') if liw else ''}")
        if liw and getattr(liw, 'is_focusable', False) and not liw.focus:
            liw.focus = True

    def on_kbd_input_mode_change(self, mode: str, _event_kwargs: dict) -> bool:
        """ language app state change event handler.

        :param mode:            the new softinput_mode string (passed as flow key).
        :param _event_kwargs:   unused event kwargs.
        :return:                True for to confirm the language change.
        """
        self.vpo(f"MainAppBase.on_kbd_input_mode_change to {mode}")
        self.change_app_state('kbd_input_mode', mode)
        self.set_var('kbd_input_mode', mode, section=APP_STATE_SECTION_NAME)  # add optional app state var to config
        return True

    def on_lang_code(self):
        """ language code app-state-change-event-handler for to refresh kv rules. """
        self.vpo(f"KivyMainApp.on_lang_code: language got changed to {self.lang_code}")
        get_txt.switch_lang(self.lang_code)

    def on_light_theme(self):
        """ theme app-state-change-event-handler. """
        self.vpo(f"KivyMainApp.on_light_theme: theme got changed to {self.light_theme}")
        self.change_light_theme(self.light_theme)

    def on_user_preferences_open(self, _flow_id: str, _event_kwargs) -> bool:
        """ enable debug mode after clicking 3 times within 6 seconds.

        :param _flow_id:        new flow id.
        :param _event_kwargs:   optional event kwargs; the optional item with the key `popup_kwargs`
                                will be passed onto the `__init__` method of the found Popup class.
        :return:                False for :meth:`~.on_flow_change` get called, opening user preferences popup.

        """
        def _timeout_reset(_dt: float):
            self._debug_enable_clicks = 0

        if self.debug_level == DEBUG_LEVEL_DISABLED:
            self._debug_enable_clicks += 1
            if self._debug_enable_clicks >= 3:
                self.debug_level: int = DEBUG_LEVEL_ENABLED
                self._debug_enable_clicks = 0
            elif self._debug_enable_clicks == 1:
                Clock.schedule_once(_timeout_reset, 6.0)

        return False

    def play_beep(self):
        """ make a short beep sound. """
        self.play_sound('error')

    def play_sound(self, sound_name: str):
        """ play audio/sound file. """
        self.vpo(f"KivyMainApp.play_sound {sound_name}")
        file: Optional[CachedFile] = self.find_sound(sound_name)
        if file:
            try:
                sound_obj = file.loaded_object
                sound_obj.pitch = file.properties.get('pitch', 1.0)
                sound_obj.volume = (
                    file.properties.get('volume', 1.0) * self.framework_app.app_states.get('sound_volume', 1.))
                sound_obj.play()
            except Exception as ex:
                self.po(f"KivyMainApp.play_sound exception {ex}")
        else:
            self.dpo(f"KivyMainApp.play_sound({sound_name}) not found")

    def play_vibrate(self, pattern: Tuple = (0.03, 0.3)):
        """ play vibrate pattern. """
        self.vpo(f"KivyMainApp.play_vibrate {pattern}")
        if self.framework_app.app_states.get('vibration_volume', 1.):   # no volume available, at least disable if 0.0
            try:        # added because is crashing with current plyer version (master should work)
                vibrator.pattern(pattern)
            # except jnius.jnius.JavaException as ex:
            #    self.po(f"KivyMainApp.play_vibrate JavaException {ex}, update plyer to git/master")
            except Exception as ex:
                self.po(f"KivyMainApp.play_vibrate exception {ex}")

    def prevent_keyboard_covering(self, input_box_bottom: float) -> bool:
        """ prevent that the virtual keyboard popping up on mobile platforms is covering the text input field.

        :param input_box_bottom:    y position of the bottom of the input field box.
        :return:                    True if keyboard is covering the passed y/bottom position, else False.
        """
        if sys_platform() != 'android':
            return False

        keyboard_height = Window.keyboard_height or Window.height / 2  # 'or'-fallback because SDL2 reports 0 kbd height
        mode_changed = input_box_bottom < keyboard_height
        Window.softinput_mode = self.kbd_input_mode if mode_changed else ''

        return mode_changed

    def setup_app_states(self, app_state: AppStateType):
        """ put app state variables into main app instance for to prepare framework app.run_app.

        :param app_state:       dict of app states.
        """
        self.vpo(f"KivyMainApp.setup_app_states {app_state}")
        if isinstance(app_state.get('font_size', None), str):
            app_state['font_size'] = sp(app_state['font_size'])     # very first app start
        super().setup_app_states(app_state)

    def show_message(self, message: str, title: str = "", is_error: bool = True):
        """ display (error) message popup to the user.

        :param message:         message string to display.
        :param title:           title of message box.
        :param is_error:        pass False to not emit error tone/vibration.
        """
        if is_error:
            self.play_vibrate(ERROR_VIBRATE_PATTERN)
            self.play_beep()

        popup_kwargs = dict(message=message)
        if title:
            popup_kwargs['title'] = title

        self.change_flow(id_of_flow('show', 'message'), popup_kwargs=popup_kwargs)

    def show_popup(self, popup_class: Type[Union[Popup, DropDown]], **popup_attributes) -> Widget:
        """ open Popup or DropDown using the `open` method. Overwriting the main app class method.

        :param popup_class:         class of the Popup or DropDown widget.
        :param popup_attributes:    args for to be set as attributes of the popup class instance plus an optional
                                    `parent` kwarg that will be passed as the popup parent widget arg
                                    to the popup.open method; if parent does not get passed then the root widget/layout
                                    of self.framework_app will passed into the popup.open method as the widget argument.
        :return:                    created and displayed/opened popup class instance.
        """
        self.dpo(f"KivyMainApp.show_popup {popup_class} {popup_attributes}")

        # framework_win has absolute screen coordinates and lacks x, y properties, therefore use app.root as def parent
        parent = popup_attributes.pop('parent', self.framework_root)
        popup_instance = popup_class(**popup_attributes)
        if self.prevent_keyboard_covering(popup_instance.y):
            container = getattr(popup_instance, '_container', None)
            if container:
                container.clear_widgets()                       # clear container for Popup only
            popup_instance = popup_class(**popup_attributes)    # new instance if kbd covering popup

        if not hasattr(popup_instance, 'close') and hasattr(popup_instance, 'dismiss'):
            popup_instance.close = popup_instance.dismiss       # create close() method alias for DropDown.dismiss()

        popup_instance.open(parent)

        return popup_instance
