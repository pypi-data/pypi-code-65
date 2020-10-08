import pygame as pg


class SimpleSprite:
    def __init__(self, coordinates, speed_x, speed_y, image, transparent_color=None):
        self.surf = pg.Surface(image.get_size(), pg.SRCALPHA, 32)
        if transparent_color:
            self.surf.set_colorkey(transparent_color)
        self.rect = self.surf.get_rect()
        self.rect.topleft = coordinates
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.surf.blit(image.convert_alpha(), (0, 0))

        self.jump_multiplier = 2
        self._current_jump_mul = self.jump_multiplier
        self.jump_velocity = 7
        self._current_jump_velocity = self.jump_velocity
        self.need_jump = False

    def draw(self, screen):
        screen.blit(self.surf, self.rect)

    def move_left(self):
        self.rect.x -= self.speed_x

    def move_right(self):
        self.rect.x += self.speed_x

    def move_up(self):
        self.rect.y -= self.speed_y

    def move_down(self):
        self.rect.y += self.speed_y

    def move(self, keys=None, left=True, right=True, up=True, down=True):
        if keys is None:
            keys = pg.key.get_pressed()
        if left and (keys[pg.K_LEFT] or keys[pg.K_a]):
            self.move_left()
        if right and (keys[pg.K_RIGHT] or keys[pg.K_d]):
            self.move_right()
        if up and (keys[pg.K_UP] or keys[pg.K_w]):
            self.move_up()
        if down and (keys[pg.K_DOWN] or keys[pg.K_s]):
            self.move_down()

    def jump(self):
        if self.need_jump:
            force = int(0.5 * self._current_jump_mul * self._current_jump_velocity ** 2)
            self.rect.y -= force
            self._current_jump_velocity -= 1
            if self._current_jump_velocity < 0:
                self._current_jump_mul = -self.jump_multiplier
            if self._current_jump_velocity == -self.jump_velocity - 1:
                self.need_jump = False
                self._current_jump_velocity = self.jump_velocity
                self._current_jump_mul = self.jump_multiplier

    def x(self, val=None):
        if not val:
            return self.rect.x
        self.rect.x = val

    def y(self, val=None):
        if not val:
            return self.rect.y
        self.rect.y = val

    def left(self, val=None):
        if not val:
            return self.rect.left
        self.rect.left = val

    def right(self, val=None):
        if not val:
            return self.rect.right
        self.rect.right = val

    def top(self, val=None):
        if not val:
            return self.rect.top
        self.rect.top = val

    def bottom(self, val=None):
        if not val:
            return self.rect.bottom
        self.rect.bottom = val

    def center(self, val=None):
        if not val:
            return self.rect.center
        self.rect.center = val

    def collide_sprite(self, sprite):
        return self.rect.colliderect(sprite.rect)

    def collide_rect(self, rect):
        return self.rect.colliderect(rect)

    def contains_sprite(self, sprite):
        return self.rect.contains(sprite.rect)

    def contains_rect(self, rect):
        return self.rect.contains(rect)
