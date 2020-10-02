from PyCollision2D.vector import Vector

class Rect:
    def __init__(self, pos, size):
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

        self._pos = pos
        self._size = size

    def _get_pos(self):
        return self._pos
    def _get_size(self):
        return self._size

    def _set_pos(self, pos):
        if not isinstance(pos, Vector):
            raise TypeError(f"unsupported type(s) for Rect.pos: '{type(pos)}'")
        self._pos = pos
    def _set_size(self, size):
        if not isinstance(size, Vector):
            raise TypeError(f"unsupported type(s) for Rect.size: '{type(size)}'")
        self._size = size

    pos = property(_get_pos, _set_pos)
    size = property(_get_size, _set_size)
    vel = property(_get_vel, _set_vel)

    def collides_with_point(self, point):
        if isinstance(point, tuple) or isinstance(point, list):
            if len(point) >= 2:
                point = Vector(point[0], point[1])
            else:
                raise ValueError(f"tuple or list must have length >= 2: {len(point)}")
        if not isinstance(point, Vector):
            raise TypeError(f"unsupported type(s) for Rect.collides_with_point(point): '{type(point)}'")

        inside_x = point.x >= self.pos.x and point.x < self.pos.x+self.size.x
        inside_y = point.y >= self.pos.y and point.y < self.pos.y+self.size.y
        return (inside_x and inside_y)

    def collides_with_rect(self, rect):
        if isinstance(rect, tuple) or isinstance(rect, list):
            if len(rect) >= 4:
                rect = Rect(rect[0:2], rect[2:4])
            else:
                raise ValueError(f"tuple or list must have length >= 4: {len(rect)}")
        if not isinstance(rect, Rect):
            raise TypeError(f"unsupported type(s) for Rect.collides_with_rect(rect): '{type(rect)}'")

        self_left_inside_rect_right = self.pos.x < rect.pos.x + rect.size.x
        self_right_inside_rect_left = self.pos.x + self.size.x > rect.pos.x
        self_top_inside_rect_bottom = self.pos.y < rect.pos.y + rect.size.y
        self_bottom_inside_rect_top = self.pos.y + self.size.y > rect.pos.y
        return (self_left_inside_rect_right and self_right_inside_rect_left and
                self_top_inside_rect_bottom and self_bottom_inside_rect_top)

    def dynamic_collision_with_rect(self, rect, velocity):
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

        if velocity.x == 0 and velocity.y == 0:
            return None, None, None, None

        expanded_target = Rect(
            Vector(
                rect.pos.x - self.size.x/2,
                rect.pos.y - self.size.y/2
            ),
            Vector(
                rect.size.x + self.size.x,
                rect.size.y + self.size.y
            )
        )


        from PyCollision2D.ray import Ray
        ray = Ray(
            Vector(
                self.pos.x + self.size.x/2,
                self.pos.y + self.size.y/2
            ),
            velocity
        )

        contact_point, contact_normal, t_hit_near, t_hit_far = ray.collision_point_with_rect(expanded_target)
        if contact_point:
            return contact_point, contact_normal, t_hit_near, t_hit_far
        else:
            return None, None, None, None

    def resolve_velocity_dynamic_collision_with_rect(self, rect, velocity):
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

        contact_point, contact_normal, t_hit_near, t_hit_far = self.dynamic_collision_with_rect(rect, velocity)
        if contact_point and t_hit_near < 1:
            velocity.x += contact_normal.x * abs(velocity.x) * (1-t_hit_near)
            velocity.y += contact_normal.y * abs(velocity.y) * (1-t_hit_near)

        return velocity, contact_point, contact_normal, t_hit_near, t_hit_far
