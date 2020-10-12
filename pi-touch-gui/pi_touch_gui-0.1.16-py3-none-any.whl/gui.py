import pygame

from .colors import BLACK


class Page(object):

    def __init__(self, widgets=None, background=None, function=None):
        self._widgets = [] if widgets is None else widgets

        if background is not None:
            self.background = pygame.image.load(background).convert()
        else:
            self.background = None
        self.function = function
        self._active_widget_num = -1
        self._prev_active_widget_num = 0

    def add_widgets(self, widgets):
        self._widgets += widgets

    def touch_handler(self, event, touch):
        """Update all widgets with a specific touch event, first one
            to consume it wins.
        """
        for widget in self._widgets:
            consumed, new_page = widget.event(event, touch)
            if consumed:
                return new_page

        if callable(self.function):
            return self.function(None)
        return None

    def render(self, screen):
        """Redraw all widgets to screen"""
        if self.background is not None:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(BLACK)
        for widget in self._widgets:
            widget.render(screen)

    def focus_widget(self):
        """ Wake up the focus system for gesture control.  Will always restart
        on the last widget that had focus.
        """
        self._active_widget_num = self._prev_active_widget_num

    def next_widget(self):
        self._shift_widgets(1)

    def prev_widget(self):
        self._shift_widgets(-1)

    def _shift_widgets(self, increment):
        current_widget_num = self._active_widget_num
        if current_widget_num >= 0:
            self._widgets[current_widget_num].focus(False)

        max_widget_num = len(self._widgets) - 1

        while True:
            # This will cause an infinite loop if none of the widgets can
            # take focus
            current_widget_num += increment
            if current_widget_num > max_widget_num:
                current_widget_num = 0
            elif current_widget_num < 0:
                current_widget_num = max_widget_num

            if self._widgets[current_widget_num].can_focus():
                break

        self._widgets[current_widget_num].focus(True)
        self._active_widget_num = current_widget_num
        self._prev_active_widget_num = current_widget_num


class GUI(object):
    FPS = 60
    FADE_TIME = 60
    BLACKOUT_TIME = 300
    # FADE_TIME = 5
    # BLACKOUT_TIME = 10
    BRIGHT_LEVEL = 128
    FADE_LEVEL = 16

    last_event = pygame.time.get_ticks()

    def __init__(self, touchscreen, bright=None):
        self._bright_level = self.BRIGHT_LEVEL if bright is None else bright
        self._touchscreen = touchscreen
        self._current_page = None
        self._first_page = None
        self._running = False
        self._faded = False
        self._blacked = False

        with open('/sys/class/backlight/rpi_backlight/max_brightness',
                  'r') as f:
            max_str = f.readline()
        self.max_brightness = min(int(max_str), 255)
        self.set_brightness(self._bright_level)

    def reset_display(self):
        self.last_event = pygame.time.get_ticks()

        if self._faded:
            self.set_brightness(self._bright_level)
            self.fade = False
        if self._blacked:
            self.set_light(True)
            self._blacked = False

    def set_brightness(self, level):
        level_str = f"{min(self.max_brightness, level)}\n"
        with open('/sys/class/backlight/rpi_backlight/brightness', 'w') as f:
            f.write(level_str)

    def set_light(self, on):
        if on is True:
            blank_str = "0"
        else:
            blank_str = "1"
            self._current_page = self._first_page
            self._current_page.render(self._touchscreen.surface)
        with open('/sys/class/backlight/rpi_backlight/bl_power', 'w') as f:
            f.write(blank_str)

    def run(self, page):
        self._current_page = page
        self._first_page = page
        self._running = True

        self._touchscreen.run()

        fpsClock = pygame.time.Clock()

        def handle_touches(e, t):
            self.reset_display()

            touch_result = self._current_page.touch_handler(e, t)
            if touch_result is not None:
                if isinstance(touch_result, Page):
                    self._current_page = touch_result
                else:
                    print(f"Unsupported touch result {type(touch_result)!r}")

        for touch in self._touchscreen.touches:
            touch.on_press = handle_touches
            touch.on_release = handle_touches
            touch.on_move = handle_touches

        try:
            while self._running:
                time = pygame.time.get_ticks()
                # deltaTime in seconds.
                deltaTime = (time - self.last_event) / 1000.0
                if deltaTime > self.BLACKOUT_TIME:
                    self.set_light(False)
                    self._blacked = True
                elif deltaTime > self.FADE_TIME:
                    self.set_brightness(self.FADE_LEVEL)
                    self._faded = True

                self._current_page.render(self._touchscreen.surface)
                pygame.display.flip()
                fpsClock.tick(60)
        finally:
            self.reset_display()
            print("Stopping touchscreen thread...")
            self._touchscreen.stop()

            print("Exiting GUI...")
            exit()

    def stop(self):
        self._running = False
