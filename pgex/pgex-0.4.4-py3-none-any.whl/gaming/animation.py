# import pygame as pg


class AnimationIterator:
    def __init__(self, images, frames_per_image):
        self.images = tuple(images)
        self.fpi = frames_per_image
        self.count = 0
        self.index = 0
        self.size = len(self.images)

    def __next__(self):
        if self.count < self.fpi:
            self.count += 1
            return self.images[self.index]
        self.count = 0
        self.index += 1
        if self.index == self.size:
            self.index = 0
        return next(self)

    def __iter__(self):
        return self


class SimpleAnimation:
    def __init__(self, images, coordinates=None, frames_per_image=1):
        self._animation_iter = AnimationIterator(images, frames_per_image)
        if coordinates:
            self.coordinates = coordinates

    @property
    def x(self):
        return self.coordinates[0] if self.coordinates else None

    @x.setter
    def x(self, x):
        if self.coordinates:
            self.coordinates = (x, self.coordinates[1])
        else:
            self.coordinates = (x, None)

    @property
    def y(self):
        return self.coordinates[0] if self.coordinates else None

    @y.setter
    def y(self, y):
        if self.coordinates:
            self.coordinates = (self.coordinates[0], y)
        else:
            self.coordinates = (None, y)

    def draw(self, screen, coordinates=None):
        if coordinates:
            self.coordinates = tuple(coordinates)
            screen.blit(next(self._animation_iter), coordinates)
        elif self.coordinates and None not in self.coordinates:
            screen.blit(next(self._animation_iter), self.coordinates)
        else:
            raise IndexError("No coordinates given to SimpleAnimation")

    def __str__(self):
        if self.coordinates:
            return f"SimpleAnimation(size: {self._animation_iter.size}," \
                    f"coordinates: {self.coordinates} frames per image: {self._animation_iter.fpi})"
        return f"SimpleAnimation(size: {self._animation_iter.size}, frames per image: {self._animation_iter.fpi})"


# if __name__ == "__main__":
#     i = AnimationIterator((1, 2, 3), 2)
#     for x in i:
#         print(x)
