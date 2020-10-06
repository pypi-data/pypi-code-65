#
# The Ray class represents a line and checks what it collides with. Keyword: Raycast
#

from PyCollision2D.vector import Vector
import math

class Ray:
    def __init__(self, pos, dir):
        if isinstance(pos, tuple) or isinstance(pos, list):
            if len(pos) >= 2:
                pos = Vector(pos[0], pos[1])
            else:
                raise ValueError(f"tuple or list must have length >= 2: {len(pos)}")
        if isinstance(dir, tuple) or isinstance(dir, list):
            if len(dir) >= 2:
                dir = Vector(dir[0], dir[1])
            else:
                raise ValueError(f"tuple or list must have length >= 2: {len(dir)}")

        if not isinstance(pos, Vector):
            raise TypeError(f"unsupported type(s) for Ray.pos: '{type(pos)}'")
        if not isinstance(dir, Vector):
            raise TypeError(f"unsupported type(s) for Ray.size: '{type(size)}'")

        self._pos = pos
        self._dir = dir

        self._contact_point = None
        self._contact_normal = None
        self._t_to_contact_point = None

    def _get_pos(self):
        return self._pos
    def _get_dir(self):
        return self._dir
    def _get_contact_point(self):
        return self._contact_point
    def _get_contact_normal(self):
        return self._contact_normal
    def _get_t_to_contact_point(self):
        return self._t_to_contact_point

    def _set_pos(self, pos):
        if not isinstance(pos, Vector):
            raise TypeError(f"unsupported type(s) for Ray.pos: '{type(pos)}'")
        self._pos = pos
    def _set_dir(self, dir):
        if not isinstance(dir, Vector):
            raise TypeError(f"unsupported type(s) for Ray.dir: '{type(dir)}'")
        self._dir = dir

    pos = property(_get_pos, _set_pos)
    dir = property(_get_dir, _set_dir)
    contact_point = property(_get_contact_point)
    contact_normal = property(_get_contact_normal)
    t_to_contact_point = property(_get_t_to_contact_point)

    def collision_point_rect(self, rect):
        from PyCollision2D.rect import Rect
        contact_point = Vector(None, None)
        contact_normal = Vector(None, None)

        self._contact_normal = None     # Point of contact
        self._contact_point = None      # Normal at point of contact from rectangle
        self._t_to_contact_point = None # 'Time' until contact point is reached

        # Cache division, speed up calculation
        inv_dir = Vector(
            1 / self.dir.x if self.dir.x != 0 else math.inf,
            1 / self.dir.y if self.dir.y != 0 else math.inf
        )

        # Calculate intersection with rectangle bounding axes
        t_near = (rect.pos - self.pos) * inv_dir
        t_far = (rect.pos + rect.size - self.pos) * inv_dir

        # If t_near or t_far is NaN reject
        if t_near.x == math.nan or t_near.y == math.nan:
            return False
        if t_far.x == math.nan or t_far.y == math.nan:
            return False

        # If t_near is further than t_far, swap them
        if t_near.x > t_far.x:
            t_near.x, t_far.x = t_far.x, t_near.x # Swap t_near.x and t_far.x
        if t_near.y > t_far.y:
            t_near.y, t_far.y = t_far.y, t_near.y # Swap t_near.y and t_far.y

        # Early rejection
        if t_near.x > t_far.y or t_near.y > t_far.x:
            return False

        t_hit_near = max(t_near.x, t_near.y) # Closest 'time' will be the first contact
        t_hit_far = min(t_far.x, t_far.y)    # Furthest 'time' is the contact on the opposite side

        # Reject if ray direction is pointing away from object
        if t_hit_near < 0:
            self._t_to_contact_point = t_hit_near # 'Time' until contact point is reached
            return False

        # Contact point of collision from parametric line equation
        contact_point = self.pos + t_hit_near * self.dir

        if t_near.x > t_near.y:
            if inv_dir.x < 0:
                contact_normal.x = 1
                contact_normal.y = 0
            else:
                contact_normal.x = -1
                contact_normal.y = 0
        elif t_near.x < t_near.y:
            if inv_dir.y < 0:
                contact_normal.x = 0
                contact_normal.y = 1
            else:
                contact_normal.x = 0
                contact_normal.y = -1
        elif t_near.x == rect.pos.x and t_near.y == rect.pos.y:
            contact_normal.x = -1
            contact_normal.y = -1
        elif t_near.x == rect.pos.x+rect.size.x and t_near.y == rect.pos.y:
            contact_normal.x = 1
            contact_normal.y = -1
        elif t_near.x == rect.pos.x+rect.size.x and t_near.y == rect.pos.y+rect.size.y:
            contact_normal.x = 1
            contact_normal.y = 1
        elif t_near.x == rect.pos.x and t_near.y == rect.pos.y+rect.size.y:
            contact_normal.x = -1
            contact_normal.y = 1

        self._contact_normal = contact_normal     # Point of contact
        self._contact_point = contact_point       # Normal at point of contact from rectangle
        self._t_to_contact_point = t_hit_near     # 'Time' until contact point is reached
        return True
