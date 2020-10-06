#
# The Vector class represents a position, a force or a direction.
#

class Vector:
    def __init__(self, x, y):
        ### Test if arguments are of correct type
        if not isinstance(x, int) and not isinstance(x, float) and x != None:
            raise TypeError(f"unsupported type(s) for Vector.x: '{type(x)}'")
        if not isinstance(y, int) and not isinstance(y, float) and y != None:
            raise TypeError(f"unsupported type(s) for Vector.y: '{type(y)}'")
        ###

        self._x = x
        self._y = y

    # Get methods
    def _get_x(self):
        return self._x
    def _get_y(self):
        return self._y

    # Set methods
    def _set_x(self, x):
        ### Test if arguments are of correct type
        if not isinstance(x, int) and not isinstance(x, float) and x != None:
            raise TypeError(f"unsupported type(s) for Point.x: '{type(x)}'")
        self._x = x

    def _set_y(self, y):
        ### Test if arguments are of correct type
        if not isinstance(y, int) and not isinstance(y, float) and y != None:
            raise TypeError(f"unsupported type(s) for Point.y: '{type(y)}'")
        self._y = y

    # Add get methods and set methods
    x = property(_get_x, _set_x)
    y = property(_get_y, _set_y)

    def __add__(self, value):
        ### Test if arguments are of correct type
        if isinstance(value, Vector):
            return Vector(self.x + value.x, self.y + value.y)
        elif isinstance(value, int) or isinstance(value, float):
            return Vector(self.x + value, self.y + value)
        else:
            raise TypeError(f"unsupported type(s) for operator +: '{type(value)}'")

    def __radd__(self, value):
        ### Test if arguments are of correct type
        if isinstance(value, Vector):
            return Vector(value.x + self.x, value.y + self.y)
        elif isinstance(value, int) or isinstance(value, float):
            return Vector(value + self.x, value + self.y)
        else:
            raise TypeError(f"unsupported type(s) for operator +: '{type(value)}'")

    def __sub__(self, value):
        ### Test if arguments are of correct type
        if isinstance(value, Vector):
            return Vector(self.x - value.x, self.y - value.y)
        elif isinstance(value, int) or isinstance(value, float):
            return Vector(self.x - value, self.y - value)
        else:
            raise TypeError(f"unsupported type(s) for operator +: '{type(value)}'")

    def __rsub__(self, value):
        ### Test if arguments are of correct type
        if isinstance(value, Vector):
            return Vector(value.x - self.x, value.y - self.y)
        elif isinstance(value, int) or isinstance(value, float):
            return Vector(value - self.x, value - self.y)
        else:
            raise TypeError(f"unsupported type(s) for operator +: '{type(value)}'")

    def __mul__(self, value):
        ### Test if arguments are of correct type
        if isinstance(value, Vector):
            return Vector(self.x * value.x, self.y * value.y)
        elif isinstance(value, int) or isinstance(value, float):
            return Vector(self.x * value, self.y * value)
        else:
            raise TypeError(f"unsupported type(s) for operator +: '{type(value)}'")

    def __rmul__(self, value):
        ### Test if arguments are of correct type
        if isinstance(value, Vector):
            return Vector(value.x * self.x, value.y * self.y)
        elif isinstance(value, int) or isinstance(value, float):
            return Vector(value * self.x, value * self.y)
        else:
            raise TypeError(f"unsupported type(s) for operator +: '{type(value)}'")

    def __truediv__(self, value):
        ### Test if arguments are of correct type
        if isinstance(value, Vector):
            return Vector(self.x / value.x, self.y / value.y)
        elif isinstance(value, int) or isinstance(value, float):
            return Vector(self.x / value, self.y / value)
        else:
            raise TypeError(f"unsupported type(s) for operator +: '{type(value)}'")

    def __rtruediv__(self, value):
        ### Test if arguments are of correct type
        if isinstance(value, Vector):
            return Vector(value.x / self.x, value.y / self.y)
        elif isinstance(value, int) or isinstance(value, float):
            return Vector(value / self.x, value / self.y)
        else:
            raise TypeError(f"unsupported type(s) for operator +: '{type(value)}'")
