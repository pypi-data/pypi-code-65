class Vector:
    def __init__(self, x, y):
        if not isinstance(x, int) and not isinstance(x, float) and x != None:
            raise TypeError(f"unsupported type(s) for Vector.x: '{type(x)}'")
        if not isinstance(y, int) and not isinstance(y, float) and y != None:
            raise TypeError(f"unsupported type(s) for Vector.y: '{type(y)}'")
        self._x = x
        self._y = y

    def _get_x(self):
        return self._x
    def _get_y(self):
        return self._y

    def _set_x(self, x):
        if not isinstance(x, int) and not isinstance(x, float) and x != None:
            raise TypeError(f"unsupported type(s) for Point.x: '{type(x)}'")
        self._x = x
    def _set_y(self, y):
        if not isinstance(y, int) and not isinstance(y, float) and y != None:
            raise TypeError(f"unsupported type(s) for Point.y: '{type(y)}'")
        self._y = y

    x = property(_get_x, _set_x)
    y = property(_get_y, _set_y)
