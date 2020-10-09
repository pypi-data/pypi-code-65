from pygame import font, draw
from pgex.parameters.colors import colors


class Text:
    """ Widget that draws text on a screen
    Text of the widget can be accessed or modified through a text property
    """
    def __init__(self, text, font_path, font_size=20, font_color=colors["black"], bg_color=None, border_width=1):
        """
        :param text: str
            Text to be shown on a screen
        :param font_path: str
            Path to font which will be used to draw text
        :param font_size: int
            Size of font of a text on a screen
        :param font_color: tuple (int, int, int)
            Color of a text on a screen
        :param bg_color: tuple (int, int, int)
            Color of background
        :param border_width: int
            width of a border of background
        """
        self._text = str(text)
        self.font_size = font_size
        self.font_name = font_path
        self.font_color = font_color
        self.bg_color = bg_color
        self.border_width = border_width

    def get_rect(self):
        """ Get rect of rendered text """
        text = self._render_text()
        return text.get_rect()

    def _render_text(self):
        font_type = font.Font(self.font_name, self.font_size)
        text = font_type.render(self._text, True, self.font_color)
        return text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = str(text)

    def draw(self, screen, coordinates):
        """ Draw text widget on a screen with given coordinates

        :param screen: pygame screen
        :param coordinates: tuple (int, int)
            Coordinates (x, y) where text widget should be drawn
        """
        text = self._render_text()
        text_rect = text.get_rect()

        if self.bg_color:
            draw.rect(screen, self.bg_color, (coordinates[0], coordinates[1], text_rect.width, text_rect.height),
                      self.border_width)

        screen.blit(text, coordinates)

    def __str__(self):
        return f"Text(text={self._text})"
