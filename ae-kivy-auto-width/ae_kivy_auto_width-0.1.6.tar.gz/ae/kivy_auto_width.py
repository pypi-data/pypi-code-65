"""
automatic container width with opening animation for kivy apps
==============================================================

This ae portion is providing the mix-in-class
:class:`ContainerChildrenAutoWidthBehavior`
for to open any container widget with an increasing
width animation and automatic detection that the
label and button texts of the container children
are fully visible/displayed.

"""
from typing import Callable

from kivy.animation import Animation                                                        # type: ignore
from kivy.core.window import Window                                                         # type: ignore
# pylint: disable=no-name-in-module
from kivy.properties import NumericProperty                                                 # type: ignore # noqa: E0611
from kivy.uix.label import Label                                                            # type: ignore
from kivy.uix.widget import Widget                                                          # type: ignore


__version__ = '0.1.6'


class ContainerChildrenAutoWidthBehavior:
    """ detect minimum width for the complete display of the textures of all children at opening with animation.

    This mix-in class can be added to any type of container or layout widget.

    A `container` attribute will be automatically created for container classes without it.

    The animation starts when the :meth:`~ContainerChildrenAutoWidthBehavior.open` method get called.
    This call will be forwarded via `super()` to the container if it has an `open` method.

    At animation start the width of this container will be set to value of the :attr:`auto_width_start`
    attribute. Then the container width increases via the running animation until, either:

    * the container width is greater than the value of the :attr:`auto_width_minimum` attribute
      and the textures of all children are fully visible or

    * the container width reaches the app window width minus the window padding specified in the
      :attr:`auto_width_window_padding` attribute.

    The window width gets bound to the container width for to ensure proper displaying if
    the window width changes.

    """
    container: Widget           #: widget to add the dynamic children to (provided by the widget to be mixed into)
    dispatch: Callable          #: event dispatch method, provided by the widget to be mixed into
    opacity: float              #: opacity of the widget to be mixed into
    width: float                #: width of the widget to be mixed into (mostly a parent of self.container)

    auto_width_anim_duration: float = NumericProperty(0.9)
    """ duration of the width animation in seconds.

    :attr:`auto_width_anim_duration` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 0.9 seconds.
    """

    auto_width_window_padding: float = NumericProperty('96sp')
    """ horizontal padding between the window and the container in pixels.

    :attr:`auto_width_window_padding` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 96sp.
    """

    auto_width_minimum: float = NumericProperty('369sp')
    """ minimum container width in pixels (before the width animation will be stopped).

    :attr:`auto_width_minimum` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 369sp.
    """

    auto_width_child_padding: float = NumericProperty('87sp')
    """ horizontal padding between child widget and child texture in pixels.

    :attr:`auto_width_child_padding` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 87sp.
    """

    auto_width_start: float = NumericProperty('3sp')
    """ container width in pixels at the start of the width animation.

    :attr:`auto_width_start` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 3sp.
    """

    _width_anim: Animation = None
    _complete_width: float = 0.0

    def __init__(self, **kwargs):
        # noinspection PyUnresolvedReferences
        self.register_event_type('on_complete_opened')  # pylint: disable=maybe-no-member
        super().__init__(**kwargs)

    def on_complete_opened(self):
        """ dispatch event when opening and width got determined. """

    def open(self, *_args, **kwargs):
        """ start optional open animation after calling open method if exists in inheriting container/layout widget.

        :param _args:           unused argument (for to have compatible signature for Popup/ModalView widgets).
        :param kwargs:          extra arguments that are removed before to be passed to the inheriting open method:

                                * 'open_width_animation': `False` will disable the `width` animation (default=True).
        """
        anim_width = kwargs.pop('open_width_animation', True)

        if callable(getattr(super(), 'open', None)):
            # noinspection PyUnresolvedReferences
            super().open(*_args, **kwargs)      # pylint: disable=maybe-no-member

        if not hasattr(super(), 'container'):
            self.container = getattr(self, '_container', self)  # Popup has _container attribute, BoxLayout=self

        if anim_width:
            container_max_width = Window.width - self.auto_width_window_padding
            self._width_anim = Animation(opacity=1.0, width=container_max_width,
                                         t='in_out_sine', d=self.auto_width_anim_duration)
            self._width_anim.bind(on_progress=self._open_width_progress)
            self._width_anim.bind(on_complete=self._on_complete_opened)
            self.width = self.auto_width_start
            self._width_anim.start(self)
        else:
            self._win_width_bind()

    def reset_width_detection(self):
        """ call to reset the last detected minimum container width (e.g. if the children text got changed). """
        self._complete_width = 0.0

    # internal methods

    def _detect_complete_width(self) -> float:
        """ check clients textures until widest child texture got detected.

        :return:                0.0 until complete width got detected, then the last detected minimum container width.
        """
        if not self._complete_width:
            if all(chi.texture_size[0] + self.auto_width_child_padding < self.width
                   for chi in self.container.children if isinstance(chi, Label)):
                self._complete_width = self.width
        return self._complete_width

    def _on_complete_opened(self, *_args):
        """ open animation completion callback/event. """
        self.opacity = 1.0
        self._win_width_bind()
        self.dispatch('on_complete_opened')

    def _on_win_width(self, *_args):
        """ Window.width event handler. """
        self.width = min(max(self.auto_width_minimum, Window.width),
                         self._detect_complete_width() or Window.width - self.auto_width_window_padding)

    def _open_width_progress(self, _anim: Animation, _self: Widget, _progress: float):
        """ animation on_progress event handler. """
        if self.width > self.auto_width_minimum:
            if self._detect_complete_width():
                self._width_anim.stop(self)

    def _win_width_bind(self):
        """ bind :class:`~kivy.core.window.Window` width property to container width. """
        Window.bind(width=self._on_win_width)
