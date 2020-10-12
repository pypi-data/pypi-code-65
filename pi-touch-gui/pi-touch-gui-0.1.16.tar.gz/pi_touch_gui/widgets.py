import math
from abc import ABC, abstractmethod

import pygame

from .colors import WHITE, BLACK, MEDIUM_GRAY
from .multitouch.raspberrypi_ts import TS_PRESS, TS_RELEASE, TS_MOVE

FONT_NAME = None


class IWidget(ABC):
    _font_cache = dict()

    def __init__(self, position, size,
                 font_size=None,
                 label=None,
                 color1=None,
                 color2=None,
                 label_color1=None,
                 label_color2=None,
                 function=None):
        """ Widget Base Class

        Parameter meanings may vary slighly by base class:

        Parameters
        ----------
        position : Tuple(x, y)
            Top-right corner of the widget
        size : Tuple(w, h)
            Size width, height of widget extent.  Note that in some widgets
            labels or indicators could fall outside of these extents.
        font_size : Integer
            Height of font in pixels.  If not specified, will be 1/2 the height
            of the widget.
        label : String
        color1 : Tuple(r,g,b,[a]) or pygame.Color
            Main color of the widget; unselected color or foreground color
        color2 : Tuple(r,g,b,[a]) or pygame.Color
            Secondary color of the widget; selected color or background color
        label_color1 : Tuple(r,g,b,[a]) or pygame.Color
            Main color of the label; unselected color
        label_color2 : Tuple(r,g,b,[a]) or pygame.Color
            Secondary color of the label; selected color
        function : callable
            Use depends on widget; the function to call on widget activation,
            or the function to call to provide data for the widget.
        """
        self.x, self.y = position
        self.w, self.h = size

        self.label = "" if label is None else label
        self.function = function
        self.color1 = MEDIUM_GRAY if color1 is None else color1
        self.color2 = WHITE if color2 is None else color2
        self.label_color1 = WHITE if label_color1 is None else label_color1
        self.label_color2 = BLACK if label_color2 is None else label_color2

        self.font_size = int(
            min(self.w, self.h) >> 1) if font_size is None else font_size
        font_key = f"{FONT_NAME}:{self.font_size}"
        if font_key in self._font_cache:
            font = self._font_cache[font_key]
        else:
            font = pygame.font.Font(FONT_NAME, self.font_size)
            self._font_cache[font_key] = font
        self.font = font
        self._focus = False

        self.touches = []
        try:
            callable(self.on_press)
        except AttributeError:
            self.on_press = None
        try:
            callable(self.on_release)
        except AttributeError:
            self.on_release = None
        try:
            callable(self.on_move)
        except AttributeError:
            self.on_move = None

    @property
    def position(self):
        return (self.x, self.y)

    @property
    def size(self):
        return (self.w, self.h)

    @property
    def pressed(self):
        return len(self.touches) > 0

    @abstractmethod
    def render(self, surface):
        """ Render to the device pygame Surface
        """

    def focus(self, enabled):
        """ Enable or disable this widget.
        """
        self._focus = enabled

    def can_focus(self):
        """ Return True if this widget can accept focus.
        """
        return True

    def touch_inside(self, touch):
        """
        Test a touch against a generic Widget rectangle

        :param touch: Tuple(x, y)
        :return: Boolean
        """
        x, y = touch.position
        if x >= self.x and x <= self.x + self.w:
            if y >= self.y and y <= self.y + self.h:
                return True
        return False

    def event(self, event, touch):
        """
        Handle touch events

        Parameters
        ----------
        event : Integer
            Event code defined for the touchscreen
        touch : Tuple(x, y)

        Returns
        -------
        Page
            The page to transition to, or None to stay on this page
        """
        # PRESS
        # A press can only be registered when it is in the widget bounds
        if self.touch_inside(touch):
            if event == TS_PRESS and touch not in self.touches:
                self.touches.append(touch)
                if callable(self.on_press):
                    return True, self.on_press(event, touch)

        # RELEASE
        # A touch can be released even when its not over a widget.
        if event == TS_RELEASE and touch in self.touches:
            self.touches.remove(touch)
            if callable(self.on_release):
                return True, self.on_release(event, touch)

        # MOVE
        # Touch movement is tracked even when it's not over a widget
        if event == TS_MOVE and touch in self.touches:
            if callable(self.on_move):
                return True, self.on_move(event, touch)
        return False, None

    def state_colors(self, active=None):
        active = self.pressed if active is None else active
        if active or self._focus:
            color = self.color2
            label_color = self.label_color2
        else:
            color = self.color1
            label_color = self.label_color1
        return color, label_color

    def render_centered_text(self, surface, text, color, bg_color=None):
        if text is None:
            return

        text = self.font.render(text, 1, color, bg_color)
        textpos = text.get_rect()
        textpos.centerx = self.x + (self.w / 2)
        textpos.centery = self.y + (self.h / 2)
        surface.blit(text, textpos)


class Label(IWidget):

    def __init__(self, position, size,
                 font_size=None,
                 label=None,
                 label_color=None):
        font_size = size[1] if font_size is None else font_size

        super(Label, self).__init__(position, size, font_size,
                                    label, label_color1=label_color,
                                    label_color2=label_color)

    def render(self, surface):
        color, label_color = self.state_colors()

        self.render_centered_text(surface, self.label, label_color)

    def can_focus(self):
        return False


class Button(IWidget):

    def __init__(self, position, size,
                 font_size=None,
                 label=None,
                 color1=None,
                 color2=None,
                 label_color1=None,
                 label_color2=None,
                 function=None):
        super(Button, self).__init__(position, size,
                                     font_size, label,
                                     color1, color2,
                                     label_color1, label_color2,
                                     function)

    def on_release(self, event, touch):
        if callable(self.function):
            return self.function(self)

    def render(self, surface):
        color, label_color = self.state_colors()

        pygame.draw.rect(surface, color, (self.position, self.size), 0)
        self.render_centered_text(surface, self.label, label_color, color)


class RoundedButton(Button):
    BUTTON = 0
    LTAB = 1
    RTAB = 2

    def __init__(self, position, size,
                 font_size=None,
                 label=None,
                 color1=None,
                 color2=None,
                 label_color1=None,
                 label_color2=None,
                 button_type=None,
                 function=None):

        super(RoundedButton, self).__init__(position, size,
                                            font_size, label,
                                            color1, color2,
                                            label_color1, label_color2,
                                            function)

        self.button_type = self.BUTTON if button_type is None else button_type

    def render(self, surface):
        color, label_color = self.state_colors()

        radius = int(self.h / 2)
        inset_x = radius if self.button_type in (self.BUTTON, self.LTAB) else 0
        inset_w = radius if self.button_type in (self.BUTTON, self.RTAB) else 0
        inset_w = inset_w + inset_x
        subrect = ((self.x + inset_x, self.y),
                   (self.w - inset_w, self.h))
        pygame.draw.rect(surface, color, subrect, 0)
        if self.button_type in (self.BUTTON, self.LTAB):
            pygame.draw.circle(surface, color,
                               (self.x + radius, self.y + radius),
                               radius)
        if self.button_type in (self.BUTTON, self.RTAB):
            pygame.draw.circle(surface, color,
                               (self.x + self.w - radius, self.y + radius),
                               radius)

        self.render_centered_text(surface, self.label, label_color, color)


class GraphButton(Button):
    LABEL_INSET = 5

    def __init__(self, position, size,
                 font_size=None,
                 label=None,
                 color1=None,
                 color2=None,
                 label_color1=None,
                 label_color2=None,
                 update=None,
                 function=None):

        super(GraphButton, self).__init__(position, size,
                                          font_size, label,
                                          color1, color2,
                                          label_color1, label_color2,
                                          function)

        self.update = update
        if self.update is None:
            self.graph_font = pygame.font.Font(FONT_NAME,
                                               int(self.h / 2.5 + 0.5))
        else:
            samples = self.update(1)
            ratio_h = max(2.5, len(samples))
            self.graph_font = pygame.font.Font(FONT_NAME,
                                               int(self.h / ratio_h + 0.5))

    def render(self, surface):
        color, label_color = self.state_colors()

        text = self.font.render(self.label, 1, label_color)
        textpos = text.get_rect()
        textpos.left = self.x + self.LABEL_INSET
        textpos.centery = self.y + (self.h / 2)

        text_width = textpos.w + self.LABEL_INSET * 2
        text_size = (text_width, self.h + 1)
        pygame.draw.rect(surface, color, (self.position, text_size))

        graph_pos = (self.x + text_width, self.y)
        graph_size = (self.w - text_width, self.h)
        pygame.draw.rect(surface, color, (graph_pos, graph_size), 2)

        surface.blit(text, textpos)

        if self.update is None:
            return

        values = self.update(graph_size[0] - 2)
        min_val = 9999
        max_val = -9999
        for entry in values:
            data = entry["data"]
            if len(data) > 0:
                min_val = entry.get("min", min(min_val, min(data)))
                max_val = entry.get("min", max(max_val, max(data)))
            else:
                min_val = 0
                max_val = 0

        range = max_val - min_val
        if range < 1:
            min_val -= 1
            max_val += 1
            range = 2

        for entry in values:
            color = entry["color"]
            data = entry["data"]

            def scale_y_value(value):
                center_val = value - (range / 2)
                return self.y + (self.h / 2 - (
                        (center_val - min_val) / range) * self.h)

            # Need two data points to start the graph
            if len(data) > 1:
                prev_y = scale_y_value(data[0])
                prev_x = graph_pos[0]
                for val in data:
                    x = prev_x + 1
                    y = scale_y_value(val)
                    pygame.draw.line(surface, color, (prev_x, prev_y), (x, y), 2)
                    prev_x = x
                    prev_y = y

                text = self.graph_font.render(snapped_value_string(data[-1], 0.1),
                                              1,
                                              color)
                textpos = text.get_rect()
                textpos.right = (self.x + self.w) - self.LABEL_INSET
                # The text tracks the graph line, unless it's outside the
                # extents, then we clamp it to inside.
                if (prev_y + textpos.h + self.LABEL_INSET) > (self.y + self.h):
                    textpos.bottom = prev_y - self.LABEL_INSET
                elif (prev_y - textpos.h - self.LABEL_INSET) < (self.y):
                    textpos.top = prev_y + self.LABEL_INSET
                else:
                    textpos.centery = prev_y
                surface.blit(text, textpos)


class IDynamicWidget(IWidget):

    def __init__(self, position, size,
                 font_size=None,
                 label=None,
                 color1=None,
                 color2=None,
                 label_color1=None,
                 label_color2=None,
                 min_max=None,
                 start_value=None,
                 snap_value=None,
                 dynamic=None,
                 function=None):

        super(IDynamicWidget, self).__init__(position, size,
                                             font_size, label,
                                             color1, color2,
                                             label_color1, label_color2,
                                             function)

        self.snap_value = 1 if snap_value is None else snap_value
        self.snap_value = 0.01 if self.snap_value < 0.01 else self.snap_value

        self.min_val, self.max_val = (min_max)
        # Value is 0..1, where adjusted_value is in the min_max range
        self.range = self.max_val - self.min_val
        self.adjusted_value = self.min_val if start_value is None else start_value
        self.value = (self.adjusted_value - self.min_val) / self.range

        self.dynamic = False if dynamic is None else True

    def map_value_to_adjusted_value(self, value):
        # map [0, 1] to [min_val, max_val] with snap
        interp_value = float(self.min_val + (self.range * value))
        return int(interp_value / self.snap_value + 0.5) * self.snap_value

    def value_str(self):
        return snapped_value_string(self.adjusted_value, self.snap_value)

    def on_release(self, event, touch):
        if self.function is not None:
            self.function(self.adjusted_value)

    def on_move(self, event, touch):
        if self.dynamic and self.function is not None:
            self.function(self.adjusted_value)


class Dial(IDynamicWidget):

    def __init__(self, position, size,
                 font_size=None,
                 label=None,
                 color1=None,
                 color2=None,
                 label_color=None,
                 min_max=None,
                 start_value=None,
                 snap_value=None,
                 dynamic=None,
                 function=None):

        if isinstance(size, tuple):
            diameter = min(size[0], size[1])
        else:
            diameter = size * 2
        radius = diameter >> 1
        font_size = (radius >> 1) if font_size is None else font_size
        super(Dial, self).__init__(position, (diameter, diameter),
                                   font_size, label,
                                   color1, color2,
                                   label_color, label_color,
                                   min_max, start_value, snap_value,
                                   dynamic, function)
        self.radius = radius
        self.cx, self.cy = self.x + radius, self.y + radius

    def on_move(self, event, touch):
        if len(self.touches) > 1:
            return

        x, y = touch.position

        dx = x - self.cx
        dy = y - self.cy

        # Value is from 0.0 to 1.0 (percent of range)
        self.value = (math.atan2(dy, dx) % math.tau) / math.tau
        self.adjusted_value = self.map_value_to_adjusted_value(self.value)

        super(Dial, self).on_move(event, touch)

    def touch_inside(self, touch):
        x, y = touch.position
        distance = math.hypot(x - self.cx, y - self.cy)
        if distance <= self.radius:
            return True

        return False

    def render(self, surface):

        wedge_rect = (self.x, self.y, self.w, self.h)
        handle_pos = (
            int(self.cx + (self.radius * math.cos(self.value * math.tau))),
            int(self.cy + (self.radius * math.sin(self.value * math.tau))))

        center = (self.cx, self.cy)
        pygame.draw.circle(surface, self.color1, center, self.radius, 0)
        pygame.draw.arc(surface, self.color2, wedge_rect,
                        -self.value * math.tau, 0.0,
                        int(self.radius * 0.5))
        pygame.draw.line(surface, self.label_color1, center, handle_pos,
                         3)
        pygame.draw.circle(surface, self.label_color1, handle_pos,
                           int(self.radius * 0.1), 0)

        self.render_centered_text(surface, self.value_str(),
                                  self.label_color1, self.color1)


class Slider(IDynamicWidget):

    def __init__(self, position, size,
                 font_size=None,
                 label=None,
                 color1=None,
                 color2=None,
                 label_color=None,
                 min_max=None,
                 start_value=None,
                 snap_value=None,
                 dynamic=None,
                 function=None):

        super(Slider, self).__init__(position, size,
                                     font_size, label,
                                     color1, color2,
                                     label_color, label_color,
                                     min_max, start_value, snap_value,
                                     dynamic, function)

    def on_move(self, event, touch):
        if len(self.touches) > 1:
            return

        x, y = touch.position

        # Compute X/Y relative to the button
        x -= self.x
        y -= self.y

        if self.w > self.h:  # Horizontal Slider
            if x >= 0 and x <= self.w:
                self.value = float(x) / float(self.w)

        elif self.h > self.w:  # Vertical Slider
            if y >= 0 and y <= self.h:
                self.value = (self.h - float(y)) / float(self.h)

        self.adjusted_value = self.map_value_to_adjusted_value(self.value)

        super(Slider, self).on_move(event, touch)

    def render(self, surface):
        pygame.draw.rect(surface, self.color1, (self.position, self.size), 0)

        if self.w > self.h:
            value_w = int(self.w * self.value)
            value_x = self.x + value_w
            pygame.draw.rect(surface, self.color2,
                             ((self.x, self.y), (value_w, self.h)))
            pygame.draw.line(surface, self.label_color1,
                             (value_x, self.y), (value_x, self.y + self.h),
                             3)

        elif self.h > self.w:
            value_h = int(self.h * self.value)
            value_y = self.y + (self.h - value_h)
            pygame.draw.rect(surface, self.color2,
                             ((self.x, value_y), (self.w, value_h)))
            pygame.draw.line(surface, self.label_color1,
                             (self.x, value_y), (self.x + self.w, value_y),
                             3)

        pygame.draw.rect(surface, self.color2, (self.position, self.size),
                         3)

        self.render_centered_text(surface, self.value_str(), self.label_color1)


class Indicator(IWidget):

    def __init__(self, position, size,
                 font_size=None,
                 label=None,
                 color1=None,
                 color2=None,
                 label_color1=None,
                 label_color2=None,
                 function=None):

        if color1 is None:
            self.box = False
            font_size = size[1] if font_size is None else font_size
        else:
            self.box = True
            font_size = (size[1] >> 1) if font_size is None else font_size

        super(Indicator, self).__init__(position, size,
                                        font_size, label,
                                        color1, color2,
                                        label_color1, label_color2,
                                        function)

    def render(self, surface):
        if callable(self.function):
            active, label = self.function()
        else:
            active, label = None, None
        label = self.label if label is None else label

        color, label_color = self.state_colors(active=active)

        if self.box:
            pygame.draw.rect(surface, color, (self.position, self.size), 0)

        self.render_centered_text(surface, label, label_color)

    def can_focus(self):
        return False


def snapped_value_string(value, snap):
    if snap < 0.1:
        val_str = f"{value:0.2f}"
    elif snap < 1:
        val_str = f"{value:0.1f}"
    else:
        val_str = f"{int(value)}"
    return val_str
