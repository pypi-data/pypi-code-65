#
# The Rect class represents an axis aligned rectangle.
#

from PyCollision2D.vector import Vector
import sys
USE_PYGAME = False
if 'pygame' in sys.modules:
    USE_PYGAME = True
    import pygame

class Rect:

    def create_rect_from_pygame_rect(rect):
            if USE_PYGAME:
                if isinstance(rect, pygame.Rect):
                    return Rect(rect.topleft, rect.size)
                else:
                    raise TypeError('Rect needs to be of type pygame.Rect')
            else:
                raise ImportError('Pygame is not imported')

    def create_pygame_rect_from_rect(rect):
        if USE_PYGAME:
            if isinstance(rect, Rect):
                return pygame.Rect(rect.pos.x, rect.pos.y, rect.size.x, rect.size.y)
            else:
                raise TypeError('Rect needs to be of type PyCollision2D.Rect')
        else:
            raise ImportError('Pygame is not imported')

    def __init__(self, pos, size):
        ### Test if arguments are of correct type
        if isinstance(pos, tuple) or isinstance(pos, list):
            if len(pos) >= 2:
                pos = Vector(pos[0], pos[1])
            else:
                raise ValueError(f"tuple or list must have length >= 2: {len(pos)}")
        if isinstance(size, tuple) or isinstance(size, list):
            if len(size) >= 2:
                size = Vector(size[0], size[1])
            else:
                raise ValueError(f"tuple or list must have length >= 2: {len(size)}")

        if not isinstance(pos, Vector):
            raise TypeError(f"unsupported type(s) for Rect.pos: '{type(pos)}'")
        if not isinstance(size, Vector):
            raise TypeError(f"unsupported type(s) for Rect.size: '{type(size)}'")
        ###

        self._pos = pos
        self._size = size
        self._center = self.pos + self.size/2
        self._ray = None

    # Get methods
    def _get_pos(self):
        return self._pos
    def _get_size(self):
        return self._size
    def _get_center(self):
        return self._center
    def _get_ray(self):
        return self._ray

    # Set methods
    def _set_pos(self, pos):
        # Test if pos is Vector
        if not isinstance(pos, Vector):
            raise TypeError(f"unsupported type(s) for Rect.pos: '{type(pos)}'")
        self._pos = pos
        self._center = self.pos + self.size/2
    def _set_size(self, size):
        # Test if size is Vector
        if not isinstance(size, Vector):
            raise TypeError(f"unsupported type(s) for Rect.size: '{type(size)}'")
        self._size = size
        self._center = self.pos + self.size/2

    # Add get methods and set methods
    pos = property(_get_pos, _set_pos)
    size = property(_get_size, _set_size)
    center = property(_get_center)
    ray = property(_get_ray)

    # Test if point is inside rect
    def collides_with_point(self, point):
        ### Test if arguments are of correct type
        if isinstance(point, tuple) or isinstance(point, list):
            if len(point) >= 2:
                point = Vector(point[0], point[1])
            else:
                raise ValueError(f"tuple or list must have length >= 2: {len(point)}")
        if not isinstance(point, Vector):
            raise TypeError(f"unsupported type(s) for Rect.collides_with_point(point): '{type(point)}'")
        ###

        inside_x = point.x >= self.pos.x and point.x < self.pos.x+self.size.x
        inside_y = point.y >= self.pos.y and point.y < self.pos.y+self.size.y
        return (inside_x and inside_y)

    # Test if self overlaps with another rect
    def collides_with_rect(self, rect):
        ### Test if arguments are of correct type
        if isinstance(rect, tuple) or isinstance(rect, list):
            if len(rect) >= 4:
                rect = Rect(rect[0:2], rect[2:4])
            else:
                raise ValueError(f"tuple or list must have length >= 4: {len(rect)}")
        if not isinstance(rect, Rect):
            raise TypeError(f"unsupported type(s) for Rect.collides_with_rect(rect): '{type(rect)}'")
        ###

        # Test if rect overlaps or not, based on sides
        left_inside_rect_right = self.pos.x < rect.pos.x + rect.size.x
        right_inside_rect_left = self.pos.x + self.size.x > rect.pos.x
        top_inside_rect_bottom = self.pos.y < rect.pos.y + rect.size.y
        bottom_inside_rect_top = self.pos.y + self.size.y > rect.pos.y

        return (left_inside_rect_right and right_inside_rect_left and
                top_inside_rect_bottom and bottom_inside_rect_top)

    # Test if moving rect will overlap with self
    def dynamic_collision_with_rect(self, rect, velocity):
        ### Test if arguments are of correct type
        if isinstance(rect, tuple) or isinstance(rect, list):
            if len(rect) >= 4:
                rect = Rect(rect[0:2], rect[2:4])
            else:
                raise ValueError(f"tuple or list must have length >= 4: {len(rect)}")
        if isinstance(velocity, tuple) or isinstance(velocity, list):
            if len(velocity) >= 2:
                velocity = Vector(velocity[0], velocity[1])
            else:
                raise ValueError(f"tuple or list must have length >= 2: {len(velocity)}")
        if not isinstance(rect, Rect):
            raise TypeError(f"unsupported type(s) for Rect.dynamic_collision_with_rect(rect, velocity): '{type(rect)}'")
        if not isinstance(velocity, Vector):
            raise TypeError(f"unsupported type(s) for Rect.dynamic_collision_with_rect(rect, velocity): '{type(velocity)}'")
        ###

        # Reject early if rect is not moving
        if velocity.x == 0 and velocity.y == 0:
            return False

        # Expand target so it can be checked from the center of self
        expanded_target = Rect(
            rect.pos - self.size/2,
            rect.size + self.size
        )

        # Use a Raycast to check if and how they overlap
        from PyCollision2D.ray import Ray
        ray = Ray(
            self.pos + self.size/2,
            velocity
        )
        if ray.collision_point_rect(expanded_target):
            self._ray = ray
            return True
        else:
            return False

    # Change velocity if rect will overlap, return altered or unaltered velocity
    def resolve_dynamic_collision_with_rect(self, rect, velocity):
        ### Test if arguments are of correct type
        if isinstance(rect, tuple) or isinstance(rect, list):
            if len(rect) >= 4:
                rect = Rect(rect[0:2], rect[2:4])
            else:
                raise ValueError(f"tuple or list must have length >= 4: {len(rect)}")
        if isinstance(velocity, tuple) or isinstance(velocity, list):
            if len(velocity) >= 2:
                velocity = Vector(velocity[0], velocity[1])
            else:
                raise ValueError(f"tuple or list must have length >= 2: {len(velocity)}")
        if not isinstance(rect, Rect):
            raise TypeError(
            f"unsupported type(s) for Rect.resolve_dynamic_collision_with_rect(rect, velocity): '{type(rect)}'"
            )
        if not isinstance(velocity, Vector):
            raise TypeError(
            f"unsupported type(s) for Rect.resolve_dynamic_collision_with_rect(rect, velocity): '{type(velocity)}'"
            )
        ###

        # Test if there is a contact point and it is not longer than the movement,
        # if so change velocity
        if self.dynamic_collision_with_rect(rect, velocity):
            if self.ray.t_to_contact_point < 1:
                velocity.x += (self._ray.contact_normal.x or 0) * abs(velocity.x) * (1-self._ray.t_to_contact_point)
                velocity.y += (self._ray.contact_normal.y or 0) * abs(velocity.y) * (1-self._ray.t_to_contact_point)

        # Return altered or unaltered velocity
        return velocity
