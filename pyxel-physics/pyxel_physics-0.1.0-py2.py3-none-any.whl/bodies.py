"""
Easier factory functions for creating Pymunk objects.
"""
import pymunk
import pyxel
from pymunk import Circle, Segment, Poly

from . import draw as _draw

DEFAULT_SPACE = None
MOMENT_MULTIPLIER = 5.0


#
# Basic geometric shapes
#
def circ(x, y, r, **kwargs):
    """
    Creates a Pymunk body with a Circle shape attached to it.

    Args:
        x (float): Center point x coordinate
        y (float): Center point y coordinate
        r (float): Circle radius
    """
    kwargs.update(draw_func=_draw.draw_circle, shape_func=(pymunk.Circle, r))
    return _make_body((x, y), **kwargs)


def line(x1, y1, x2, y2, radius=1, **kwargs):
    """
    Creates a Pymunk body with a Segment shape attached to it.

    Args:
        x1 (float): x coordinate of starting point
        y1 (float): y coordinate of starting point
        x2 (float): x coordinate of ending point
        y2 (float): y coordinate of ending point
        radius (float): Collision radius for line element.
    """
    x = (x1 + x2) / 2
    y = (y1 + y2) / 2
    a = (x1 - x, y1 - y)
    b = (x2 - x, y2 - y)
    kwargs.update(draw_func=_draw.draw_segment, shape_func=(pymunk.Segment, a, b, radius))
    kwargs.setdefault('density', 10)
    return _make_body((x, y), **kwargs)


def tri(x1, y1, x2, y2, x3, y3, radius=0.0, **kwargs):
    """
    Creates a Pymunk body with a triangular Poly shape attached to it.

    Args:
        x1 (float): x coordinate of first point
        y1 (float): y coordinate of first point
        x2 (float): x coordinate of second point
        y2 (float): y coordinate of second point
        x3 (float): x coordinate of last point
        y3 (float): y coordinate of last point
        radius (float): Collision radius for line element.
    """
    x = (x1 + x2 + x3) / 3
    y = (y1 + y2 + y3) / 3
    vertices = [
        (x1 - x, y1 - y),
        (x2 - x, y2 - y),
        (x3 - x, y3 - y),
    ]
    kwargs.update(draw_func=_draw.draw_poly, shape_func=(pymunk.Poly, vertices, None, radius))
    return _make_body((x, y), **kwargs)


def rect(x, y, w, h, radius=0.0, **kwargs):
    """
    Creates a Pymunk body with a triangular Poly shape attached to it.

    Args:
        x (float): x coordinate of starting point
        y (float): y coordinate of starting point
        w (float): width
        h (float): height
        radius (float): Collision radius for line element.
    """
    x_ = x + w / 2
    y_ = y + h / 2
    kwargs.update(draw_func=_draw.draw_poly, shape_func=(pymunk.Poly.create_box, (w, h), radius))
    return _make_body((x_, y_), **kwargs)


def margin(x=0, y=0, width=None, height=None, col=None):
    """
    Creates a margin around the screen.
    """
    kwargs = {'col': col, 'mass': 'inf'}
    if width is None:
        width = pyxel.width - 1
    if height is None:
        height = pyxel.height - 1

    return [
        line(x, y, x + width, y, **kwargs),
        line(x + width, y, x + width, y + height, **kwargs),
        line(x + width, y + height, x, y + height, **kwargs),
        line(x, y + height, x, y, **kwargs),
    ]


def space(bg=pyxel.COLOR_BLACK, col=pyxel.COLOR_WHITE, gravity=None, damping=None):
    """
    Create a space object.

    Args:
        bg (int): Background color
        col (int): Default foreground color
        gravity (Vec2d): An optional 2-tuple with gravity coordinates
        damping (float): Damping coefficient
    """
    global DEFAULT_SPACE
    DEFAULT_SPACE = space = pymunk.Space()

    def update(dt=1 / pyxel.DEFAULT_FPS):
        space.step(dt)

    def draw(x=0, y=0, col=None, clear=False):
        if clear:
            pyxel.cls(space.bg)
        default_col = col or space.col

        for shape in space.shapes:
            try:
                draw_fn = shape.draw
            except AttributeError:
                _draw.draw(shape, x, y, default_col)
            else:
                draw_fn(x, y, col)

    def run():
        pyxel.run(update, lambda: draw(clear=True))

    space.col = col
    space.bg = bg
    space.update = update
    space.draw = draw
    space.run = run
    _setattrs(space, gravity=gravity, damping=damping)
    return space


def moment_multiplier(value=None):
    """
    Default multiplier used to calculate the moment of standard shapes.
    """
    global MOMENT_MULTIPLIER

    if value is None:
        return MOMENT_MULTIPLIER
    else:
        MOMENT_MULTIPLIER = value

#
# Utility functions
#
def _make_body(pos, shape_func, draw_func, vel=(0, 0), moment=None, mass=None,
               density=1.0,
               elasticity=1.0, friction=0.0, space=None, col=None) -> pymunk.Body:
    """
    Internal function that wraps common logic and functionality for all
    body/shape creation functions.
    """
    # Create body and shape
    body = pymunk.Body()
    body.position = pos
    body.velocity = vel

    fn, *args = shape_func
    shape = fn(body, *args)
    shape.elasticity = elasticity
    shape.friction = friction

    # Register to space, when possible
    space = space or DEFAULT_SPACE
    if space:
        space.add(body, shape)

    # Save mass and inertia
    if mass == 'inf' or mass == float('inf'):
        body.body_type = pymunk.Body.KINEMATIC
    else:
        shape.density = float(density)
        body.moment = shape.moment * MOMENT_MULTIPLIER

    # Monkey patch with a draw function
    shape.color = col

    def draw(x=0, y=0, col=None):
        if col is None and shape.color is None:
            col = _draw.FOREGROUND_COLOR
        elif col is None:
            col = shape.color
        draw_func(shape, x, y, col)

    body.draw = lambda x=0, y=0, col=None: [s.draw(x, y, col) for s in body.shapes]
    shape.draw = draw

    return body


def _setattrs(obj, **kwargs):
    """Set non-null attributes"""

    for k, v in kwargs.items():
        if v is not None:
            setattr(obj, k, v)
    return obj