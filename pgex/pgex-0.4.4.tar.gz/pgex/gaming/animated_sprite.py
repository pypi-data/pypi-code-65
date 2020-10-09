from pgex.gaming.animation import AnimationIterator
from .base_sprite import BaseSprite


class AnimatedSprite(BaseSprite):
    def __init__(self, coordinates, speed_x, speed_y, stay_images, left_images=None, right_images=None,
                 up_images=None, down_images=None, jump_images=None, transparent_color=None, frames_per_image=1):
        super().__init__(coordinates, speed_x, speed_y, stay_images[0], transparent_color)

        self.stay_animation = AnimationIterator(stay_images, frames_per_image)
        self.left_animation = AnimationIterator(left_images, frames_per_image) if left_images else self.stay_animation
        self.right_animation = AnimationIterator(right_images,
                                                 frames_per_image) if right_images else self.stay_animation
        self.up_animation = AnimationIterator(up_images, frames_per_image) if up_images else self.stay_animation
        self.down_animation = AnimationIterator(down_images, frames_per_image) if down_images else self.stay_animation
        self.jump_animation = AnimationIterator(jump_images, frames_per_image) if jump_images else self.stay_animation

    def stay(self):
        self.surf.blit(next(self.stay_animation), (0, 0))

    def move_left(self):
        super().move_left()
        self.surf.blit(next(self.left_animation), (0, 0))

    def move_right(self):
        super().move_right()
        self.surf.blit(next(self.right_animation), (0, 0))

    def move_up(self):
        super().move_up()
        self.surf.blit(next(self.up_animation), (0, 0))

    def move_down(self):
        super().move_down()
        self.surf.blit(next(self.down_animation), (0, 0))

    def move(self, keys=None, left=True, right=True, up=True, down=True):
        self.stay()
        super().move(keys, left, right, up, down)

    def jump(self):
        super().jump()
        self.surf.blit(next(self.jump_animation), (0, 0))
