from .base_sprite import BaseSprite


class SimpleSprite(BaseSprite):
    def __init__(self, coordinates, speed_x, speed_y, image, transparent_color=None):
        super().__init__(coordinates, speed_x, speed_y, image, transparent_color)
        self.surf.blit(image.convert_alpha(), (0, 0))
