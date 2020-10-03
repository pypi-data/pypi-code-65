"""
enaml application widgets, helper functions and classes
=======================================================

The enaml module `widgets` is providing widgets for to write
themed applications which can switch their font colors and
backgrounds at run-time between dark and light.

Another set of widgets provided by this namespace portion
allows the automatic change of the application flow with
only few lines of code.

For to convert colors between the enaml and other formats
the functions declared in the :mod:`functions` of this package
can be used.


main application class for GUIApp-conform Enaml app
---------------------------------------------------

The classes :class:`FrameworkApp` and :class:`EnamlMainApp`
of this ae portion are bundling and adding useful
attributes and methods for your application and are
extendable by creating a sub class.

The class :class:`EnamlMainApp` is implementing a main app
class that is reducing the amount of code needed for
to create a Python application based on the
`enaml framework <https://enaml.readthedocs.io/en/latest/>`_.

:class:`EnamlMainApp` is based on the following classes:

* the abstract base class :class:`~ae.gui_app.MainAppBase`
  which is providing :ref:`application status`
  (including :ref:`app-state-variables` and :ref:`app-state-constants`),
  :ref:`application flow` and :ref:`application events`.
* the class :class:`~ae.console.ConsoleApp` is adding
  :ref:`config-files`, :ref:`config-variables`
  and :ref:`config-options`.
* the class :class:`~ae.core.AppBase` is adding
  :ref:`application logging` and :ref:`application debugging`.


The main app class :class:`EnamlMainApp` is also encapsulating the
enaml app class for the Qt widget set (<enaml.QtApplication>)
within the :class:`FrameworkApp` class.

An instance of the Enaml app class can be directly accessed from
the main app class instance via the
:attr:`~ae.gui_app.MainAppBase.framework_app` attribute.

"""
from typing import Any, Callable, Optional, Tuple, Type

import atom.api                                                                             # type: ignore

import enaml                                                                                # type: ignore
# from enaml.application import Application

from enaml.qt import QtCore                                                                 # type: ignore
from enaml.qt.qt_application import QtApplication                                           # type: ignore

from enaml.icon import IconImage, Icon                                                      # type: ignore
from enaml.image import Image                                                               # type: ignore
from enaml.widgets.widget import Widget                                                     # type: ignore
# from enaml.widgets.popup_view import PopupView as PopupsRegister

from ae.files import CachedFile, FilesRegister                                              # type: ignore

# forward import most important flow methods for final app/project (id_of_flow, flow_action, flow_key not used here)
# noinspection PyUnresolvedReferences
from ae.gui_app import id_of_flow, flow_action, flow_key, replace_flow_action, MainAppBase  # type: ignore # noqa: F401

from .functions import ae_rgba                                                              # noqa: F401

# import `from [ae.enaml_app].widgets import...` fails with: ModuleNotFoundError: No module named 'ae.enaml_app.widgets'
# .. therefore moved these imports directly to enaml_lisz.main_view.enaml
# with enaml.imports():
#     # noinspection PyUnresolvedReferences
#     # pylint:disable=import-error
#     from ae.enaml_app.widgets import (                                                    # type: ignore # noqa: F401
#         FlowButton, FlowPopup, FontSizeEditPopup,
#         ThemeButton, ThemeContainer, ThemeField, ThemeMainWindow,
#         UserPreferencesOpenPopup)


__version__ = '0.1.15'


COMMAND_KEYS = {
    QtCore.Qt.Key_Escape:       'escape',
    QtCore.Qt.Key_Tab:          'tab',
    QtCore.Qt.Key_Backspace:    'backspace',
    QtCore.Qt.Key_Delete:       'del',
    QtCore.Qt.Key_Enter:        'enter',
    QtCore.Qt.Key_Return:       'enter',
    QtCore.Qt.Key_Up:           'up',
    QtCore.Qt.Key_Down:         'down',
    QtCore.Qt.Key_Right:        'right',
    QtCore.Qt.Key_Left:         'left',
    QtCore.Qt.Key_Home:         'home',
    QtCore.Qt.Key_End:          'end',
    QtCore.Qt.Key_PageUp:       'pgup',
    QtCore.Qt.Key_PageDown:     'pgdown',
}


def convert_key_event_to_code(event) -> Tuple[str, str]:
    """ converts the Qt key-press/-release event into a modifiers and key code string. """
    mod_flag = int(event.modifiers())
    mod_parts = list()
    if mod_flag & QtCore.Qt.AltModifier:
        mod_parts.append('Alt')
    if mod_flag & QtCore.Qt.ControlModifier:
        mod_parts.append('Ctrl')
    if mod_flag & QtCore.Qt.MetaModifier:
        mod_parts.append('Meta')
    if mod_flag & QtCore.Qt.ShiftModifier:
        mod_parts.append('Shift')
    modifiers = "".join(mod_parts)

    key_code = event.key()
    return modifiers, COMMAND_KEYS.get(key_code) or event.text() or str(key_code)


class FrameworkApp(QtApplication):
    """ enaml framework application class with atom member/attribute support. """
    app_state_flow_id = atom.api.Str()
    app_state_flow_path = atom.api.ContainerList()
    app_state_font_size = atom.api.Float()
    app_state_light_theme = atom.api.Bool()
    app_state_sound_volume = atom.api.Float()
    app_state_win_rectangle = atom.api.Tuple()

    app_state_flow_id_ink = atom.api.Tuple()
    app_state_flow_path_ink = atom.api.Tuple()
    app_state_selected_item_ink = atom.api.Tuple()
    app_state_unselected_item_ink = atom.api.Tuple()

    # shortcut attributes (indirectly saved as app states)
    landscape = atom.api.Bool()         # saved via win_rectangle app state


class EnamlMainApp(MainAppBase):
    """ enaml application main base class """
    flow_id_ink: tuple = (0.99, 0.99, 0.69, 0.69)           #: rgba color tuple for drag&drop node placeholder
    flow_path_ink: tuple = (0.99, 0.99, 0.39, 0.48)         #: rgba color tuple for drag&drop item placeholder
    selected_item_ink: tuple = (0.69, 1.0, 0.39, 0.18)      #: rgba color tuple for list items (selected)
    unselected_item_ink: tuple = (0.39, 0.39, 0.39, 0.18)   #: rgba color tuple for list items (unselected)

    _original_key_press_handler: Optional[Callable] = None
    _original_key_release_handler: Optional[Callable] = None
    _original_win_resize_handler: Optional[Callable] = None

    # implementation of abstract method

    def init_app(self, framework_app_class: Type[FrameworkApp] = FrameworkApp
                 ) -> Tuple[Optional[Callable], Optional[Callable]]:
        """ initialize framework app instance and root window/layout, return GUI event loop start/stop methods. """

        # tried to fix pytest problem: re-use Application._instance instead of resetting it:
        # try:
        #     self.framework_app = framework_app_class()
        # except RuntimeError:
        #     self.framework_app = Application.instance()
        #     print(f"EnamlMainApp.init_app: re-using app instance {self.framework_app}")
        self.framework_app = framework_app_class()

        with enaml.imports():
            # pylint:disable=import-error,import-outside-toplevel
            # noinspection PyUnresolvedReferences
            from main_view import Main              # type: ignore

        self.framework_win = Main(app=self.framework_app, main_app=self)
        self.framework_win.title = self.app_title

        self.framework_win.observe('closed', self.win_closed)

        def _event_loop_start():
            """ start event loop and ensure on_app_run event is firing when event loop is started (setting focus). """
            # QtCore.QTimer().singleShot(0, partial(self.call_method, 'on_enaml_app_start'))  # pylint:disable=no-member
            self.framework_app.start()

        return _event_loop_start, self.framework_app.stop    # enaml event loop start and stop methods

    # overwritten and helper methods

    def cached_icon(self, icon_name: str, size: float, light: bool) -> Optional[Icon]:
        """ get cached image/icon object. """
        cached: Optional[CachedFile] = self.find_image(icon_name, height=size, light_theme=light)
        if cached:
            return cached.loaded_object
        return None

    def focus_widget(self, widget: Widget):
        """ set input/keyboard focus to the passed widget.

        :param widget:      widget/window that will receive the focus.
        """
        self.dpo(f"EnamlMainApp.focus_widget change focus from {self.focused_widget()} to {widget}")
        widget.set_focus()

    def focused_widget(self) -> str:
        """ enaml/qt focus debug helper method determining tool tip of the current qt widget with focus

        :return: tool tip string of current focus or app window status.
        """
        window = self.framework_win
        if not window:
            return "focused_widget:no framework_win"
        proxy = window.proxy
        if not proxy:
            return f"focused_widget:no proxy; framework_win={window}"
        widget = proxy.widget.focusWidget()
        if not widget:
            return f"focused_widget:no focus widget; proxy={proxy}"
        tip = widget.toolTip()
        if not tip:
            return f"focused_widget:empty toolTip; widget={widget}"
        return tip

    def key_press_from_enaml(self, event):
        """ convert/normalize enaml/Qt key press/down event and pass it to MainAppBase key press dispatcher. """
        modifiers, key = convert_key_event_to_code(event)
        self.dpo(f"EnamlMainApp.key_press_from_enaml '{modifiers}_{key}'")
        if not self.key_press_from_framework(modifiers, key):
            self._original_key_press_handler(event)      # type: ignore

    def key_release_from_enaml(self, event):
        """ convert/normalize enaml/Qt key release/up event and pass it to MainAppBase key release dispatcher. """
        modifiers, key = convert_key_event_to_code(event)
        self.dpo(f"EnamlMainApp.key_release_from_enaml '{modifiers}_{key}'")
        self.call_method('on_key_release', key)

    def load_images(self):
        """ overwrite un-cached image file register to use cached image files instead. """
        def load_icon(icon_file: CachedFile) -> Icon:
            """ load image file as icon object into file cache object. """
            with open(icon_file.path, 'rb') as open_fp:
                data = open_fp.read()
            img = Image(data=data)
            ico = IconImage(image=img)
            return Icon(images=[ico])

        self.image_files = FilesRegister('img/**', file_class=CachedFile, object_loader=load_icon)

    def on_app_start(self):
        """ start app event handler. """
        super().on_app_start()      # call on_app_start from lisz_app_data
        self.framework_win.initial_position = self.win_rectangle[:2]
        self.framework_win.initial_size = self.win_rectangle[2:]
        self.framework_win.show()

    def on_flow_widget_focused(self):
        """ set focus to the widget referenced by the current flow id. """
        liw = self.widget_by_flow_id(self.flow_id)
        self.dpo(f"EnamlMainApp.on_flow_widget_focused() '{self.flow_id}'"
                 f" {liw} hasFocus={liw.has_focus() if hasattr(liw, 'has_focus') else ''}")
        if liw and not liw.has_focus():
            self.focus_widget(liw)

    def play_sound(self, sound_name: str):
        """ play audio/sound file. """
        self.dpo(f"EnamlMainApp.play_sound {sound_name}")
        file = self.find_sound(sound_name)
        if file:
            try:
                # pylint:disable=no-name-in-module,import-outside-toplevel
                from PyQt5.QtMultimedia import QSoundEffect     # type: ignore
                from PyQt5.QtCore import QUrl                   # type: ignore
                # pylint:enable=no-name-in-module,import-outside-toplevel

                sound_obj = QSoundEffect()
                sound_obj.setSource(QUrl.fromLocalFile(file.path))
                sound_obj.setVolume(
                    file.properties.get('volume', 1.0) * self.framework_app.app_state_sound_volume)
                sound_obj.play()
            except Exception as ex:     # pylint:disable=broad-except
                self.po(f"   *  EnamlMainApp.play_sound({sound_name}) exception {ex}")
        else:
            self.dpo(f"EnamlMainApp.play_sound({sound_name}) not found")

    def show_popup(self, popup_class: Type, **popup_kwargs) -> Widget:
        """ open Popup and set focus to the first widget.

        :param popup_class:     class of the Popup widget/window.
        :param popup_kwargs:    args for to instantiate and show/open the popup.
        :return:                instance of the popup widget.
        """
        if 'parent' not in popup_kwargs:
            popup_kwargs['parent'] = self.framework_win

        popup_instance = super().show_popup(popup_class, **popup_kwargs)

        self.dpo(f"EnamlMainApp.show_popup instance={popup_instance} win_type={popup_instance.window_type}")
        self.focus_widget(popup_instance.children[0].children[0])    # first children[0] is the container
        return popup_instance

    def user_preference_color_selected(self, color_name: str, dialog):
        """ ColorDialog callback. """
        self.dpo(F"EnamlMainApp.user_preference_color_selected {color_name} {dialog.selected_color}")
        if dialog.selected_color:
            self.change_app_state(color_name, ae_rgba(dialog.selected_color))

    def win_activated(self, main_window: Any):
        """ main window activated event handler, called only once on app startup via widgets.enaml/ThemeMainWindow.

        :param main_window:
        :return:
        """
        qt_window = main_window.proxy.widget
        assert main_window == self.framework_win, f"win_activated {main_window} != {self.framework_win}"

        assert not self._original_key_press_handler, "win_activated has to be called only once at window open"
        self._original_key_press_handler = qt_window.keyPressEvent
        qt_window.keyPressEvent = self.key_press_from_enaml

        assert not self._original_key_release_handler, "win_activated has to be called only once at window open"
        self._original_key_release_handler = qt_window.keyReleaseEvent
        qt_window.keyReleaseEvent = self.key_release_from_enaml

        assert not self._original_win_resize_handler, "win_activated has to be called only once at window open"
        self._original_win_resize_handler = qt_window.resizeEvent
        qt_window.resizeEvent = self.win_resize_from_enaml

    def win_closed(self, changed: dict):
        """ callback fired on close of Main window for to save/restore framework_win.geometry on app exit/start.

        :param changed:    qt/enaml changed event dict.

        .. note::
            neither self.framework_app.stop() nor self.framework_app._ qapp.exit(exit_code) trigger window closed event.

        """
        self.dpo(f"EnamlMainApp.win_closed({changed}) called")

        qt_window = self.framework_win.proxy.widget
        qt_window.resizeEvent = self._original_win_resize_handler
        qt_window.keyPressEvent = self._original_key_press_handler
        qt_window.keyReleaseEvent = self._original_key_release_handler

        geo = self.framework_win.geometry()
        self.win_pos_size_change(geo.x, geo.y, geo.width, geo.height)

        self.save_app_states()
        self.call_method('on_enaml_app_stop')

    def win_resize_from_enaml(self, event):
        """ convert/normalize enaml/Qt key press/down event and pass it to MainAppBase key press dispatcher. """
        win_size = event.size()
        self.dpo(f"EnamlMainApp.win_resize_from_enaml {self.framework_app.landscape} {event.oldSize()}=>{win_size}")
        self.win_pos_size_change(*self.win_rectangle[:2], win_size.width(), win_size.height())
        self._original_win_resize_handler(event)
