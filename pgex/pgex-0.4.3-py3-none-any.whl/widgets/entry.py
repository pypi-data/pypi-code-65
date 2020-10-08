from pgex.widgets.text import Text
from pgex.parameters.colors import colors
import pygame as pg


class Entry:
    """ Widget that draws entry field on a screen
    Text of the Entry can be accessed or modified through a text property
    """
    def __init__(self, width, height, font_path, font_size=20, font_color=colors["black"], text="", centralized=False):
        """

        :param width: int
            Width of a entry drawn on a screen
        :param height: int
            Height of a entry drawn on a screen
        :param font_path: str
            Path to font which will be used to draw text
        :param font_size: int
            Size of font of a text on a screen
        :param font_color: tuple (int, int, int)
             Color of a text on a screen
        :param text: str
            Initial text to be drawn on an entry field
        :param centralized: bool
            If True - text will be printed in a center of button
        """
        self.width = width
        self.height = height
        self._text = Text(text, font_path, font_size, font_color)
        self.entering_text = False
        self.x = 0
        self.y = 0
        self.input_rect = pg.Rect(0, 0, self.width, self.height)
        self.centralized = centralized

    def draw(self, screen, coordinates, pg_events):
        """ Draw button widget on a screen with given coordinates (x, y)

        If user started input by clicking inside entry - self._get_input begins controlling widget.
        Method draws something like interaction with user. If mouse cursor hovers over entry - widget
        would be highlighted.

        :param screen: pygame screen
        :param coordinates: tuple (int, int)
            Coordinates (x, y) where entry widget should be drawn
        :param pg_events: events from pygame.event.get()
            All main events like pygame.QUIT should be handled outside this class
        """
        if self.entering_text:
            self._get_input(screen, coordinates, pg_events)
            return
        x, y = coordinates
        mouse_pos, mouse_click = pg.mouse.get_pos(), pg.mouse.get_pressed()
        if (self.x, self.y) != coordinates:
            self.input_rect = pg.Rect(x, y, self.width, self.height)
        text_coordinates = coordinates
        if self.centralized:
            text_rect = self._text.get_rect()
            text_coordinates = (x + self.width // 2 - text_rect.width // 2,
                                y + self.height // 2 - text_rect.height // 2)

        if self.input_rect.collidepoint(mouse_pos[0], mouse_pos[1]):
            if mouse_click[0]:
                self.entering_text = True
                self._get_input(screen, coordinates, pg_events)
            else:
                pg.draw.rect(screen, colors["white"], self.input_rect)
                pg.draw.rect(screen, colors["black"], (x, y, self.width, self.height), 3)
                self._text.draw(screen, text_coordinates)
        else:
            pg.draw.rect(screen, colors["white"], self.input_rect)
            pg.draw.rect(screen, colors["black"], (x, y, self.width, self.height), 1)
            self._text.draw(screen, text_coordinates)

    def _get_input(self, screen, coordinates, pg_events):
        """ Getting input from entry field

        Function takes unicodes of pressed buttons and inserts them in self._text attribute.
        Backspace button erases last symbol.
        Enter or Escape buttons stops getting input data.

        :param screen: pygame screen
        :param coordinates: tuple (int, int)
            Coordinates (x, y) where entry widget should be drawn
        :param pg_events: events from pygame.event.get()
            All main events like pygame.QUIT should be handled outside this class
        """
        x, y = coordinates
        text_coordinates = coordinates
        if self.centralized:
            text_rect = self._text.get_rect()
            text_coordinates = (x + self.width // 2 - text_rect.width // 2,
                                y + self.height // 2 - text_rect.height // 2)

        pg.draw.rect(screen, colors["white"], self.input_rect)
        pg.draw.rect(screen, colors["black"], (x, y, self.width, self.height), 5)
        self._text.draw(screen, text_coordinates)

        for event in pg_events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN or event.key == pg.K_ESCAPE:
                    self.entering_text = False
                    return
                elif event.key == pg.K_BACKSPACE:
                    self._text.text = self._text.text[:-1]
                elif self._is_ascii(event.unicode):
                    self._text.text = self._text.text + event.unicode
                    text_rect = self._text.get_rect()
                    if text_rect.width >= self.input_rect.width:
                        self._text.text = self._text.text[:-1]

        mouse_pos, mouse_click = pg.mouse.get_pos(), pg.mouse.get_pressed()
        if not self.input_rect.collidepoint(mouse_pos[0], mouse_pos[1]) and mouse_click[0]:
            self.entering_text = False

    @property
    def text(self):
        return self._text.text

    @text.setter
    def text(self, text):
        self._text.text = text

    def _is_ascii(self, s):
        """ Checks if string consists only from printable ASCII symbols

        :param s: str
            String to be checked
        :return: bool
            True if string consists of ASCII symbols. Otherwise False.
        """
        return all(ord(c) < 128 for c in s)

    def __str__(self):
        return f"Entry(text={self.text.text}, size=({self.width}x{self.height}))"
