from pgex.widgets.text import Text
from pygame import draw, mouse, mixer, time, Rect
from pgex.parameters.colors import colors


class Button:
    """ Widget that draws button on a screen """
    def __init__(self, width, height, text, font_path, font_size, sound_path=None, font_color=colors["black"],
                 inactive_bg=colors["dark_green"], active_bg=colors["green"], pressed_bg=colors["light_green"],
                 action=lambda: None, centralized=False):
        """
        :param width: int
            Width of a button drawn on a screen
        :param height: int
            Height of a button drawn on a screen
        :param text: str
            Text to be drawn on a button
        :param font_path: str
            Path to font which will be used to draw text
        :param font_size: int
            Size of font of a text on a screen
        :param sound_path: str
            Path to sound which will be played when user clicks the button
        :param font_color: tuple (int, int, int)
             Color of a text on a screen
        :param inactive_bg: tuple (int, int, int)
            Color of inactive button
        :param active_bg: tuple (int, int, int)
            Color of button when mouse cursor is on it
        :param pressed_bg: tuple (int, int, int)
            Color of button when user pressed it
        :param action: function/method name
            Function that will be called when user pressed button
        :param centralized: bool
            If True - text will be printed in a center of button
        """
        self.width = width
        self.height = height
        self.text = Text(text, font_path, font_size, font_color)
        self.action = action
        self.inactive_bg = inactive_bg
        self.active_bg = active_bg
        self.pressed_bg = pressed_bg
        self.sound = mixer.Sound(sound_path) if sound_path else None
        self.centralized = centralized

    def draw(self, screen, coordinates):
        """ Draw button widget on a screen with given coordinates

        Changes color of button when mouse is on a button or when button is clicked.
        Also, if user clicked a button, self.action would be called.

        :param screen: pygame screen
        :param coordinates: tuple (int, int)
            Coordinates (x, y) where button widget should be drawn
        """
        x, y = coordinates
        mouse_pos, mouse_click = mouse.get_pos(), mouse.get_pressed()
        button_rect = Rect(x, y, self.width, self.height)

        text_coordinates = coordinates
        if self.centralized:
            text_rect = self.text.get_rect()
            text_coordinates = (x + self.width // 2 - text_rect.width // 2,
                                y + self.height // 2 - text_rect.height // 2)

        if button_rect.collidepoint(mouse_pos[0], mouse_pos[1]):
            if mouse_click[0]:
                if self.sound:
                    self.sound.play()
                draw.rect(screen, self.pressed_bg, button_rect)
                self.text.draw(screen, text_coordinates)

                self.action()
                time.delay(200)
            else:
                draw.rect(screen, self.active_bg, button_rect)
                self.text.draw(screen, text_coordinates)
        else:
            draw.rect(screen, self.inactive_bg, button_rect)
            self.text.draw(screen, text_coordinates)

    def __str__(self):
        return f"Button(text={self.text.text}, size=({self.width}x{self.height}))"
