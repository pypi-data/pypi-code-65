"""
Draw Pymunk elements using pyxel.
"""
from functools import singledispatch

import pyxel
from pymunk import Body, Circle, Space, Segment, Poly


BACKGROUND_COLOR = pyxel.COLOR_BLACK
FOREGROUND_COLOR = pyxel.COLOR_WHITE


#
# Background/foreground drawing
#
def bg(col=None):
    """
    Get or set the default background color for space objects.
    """
    global BACKGROUND_COLOR

    if col is None:
        return BACKGROUND_COLOR
    else:
        BACKGROUND_COLOR = col


def fg(col=None):
    """
    Get or set the default foreground color for space objects.
    """
    global FOREGROUND_COLOR

    if col is None:
        return FOREGROUND_COLOR
    else:
        FOREGROUND_COLOR = col


#
# Draw Pymunk shapes 
#
@singledispatch
def draw(shape, x=0, y=0, col=None):
    """
    Draw Pymunk shape or all shapes in a Pymunk body or space with a given
    offset.

    Args:
        shape: A Pymunk shape, body or space
        x (int): x coordinate offset
        y (int): y coordinate offset
        col (int): A color index
    """
    try:
        method = shape.draw
    except AttributeError:
        name = type(shape).__name__
        raise TypeError(f'Cannot draw {name} objects')
    else:
        return method(x, y, col=col)


@singledispatch
def drawb(shape, x=0, y=0, col=None):
    """
    Like draw, but renders only the outline of a shape.

    Args:
        shape: A Pymunk shape, body or space
        x (int): x coordinate offset
        y (int): y coordinate offset
        col (int): A color index
    """
    try:
        method = shape.drawb
    except AttributeError:
        name = type(shape).__name__
        raise TypeError(f'Cannot draw {name} objects')
    else:
        return method(x, y, col=col)


#
# draw() function
#
@draw.register(Space)
def draw_space(s: Space, x=0, y=0, col=None):
    if hasattr(s, 'background'):
        pyxel.cls(s.background)
    elif BACKGROUND_COLOR is not None:
        pyxel.cls(BACKGROUND_COLOR)
    for a in s.shapes:
        draw(a, x, y, col)


@draw.register(Body)
def draw_body(b: Body, x=0, y=0, col=None):
    for s in b.shapes:
        draw(s, x, y, col)


@draw.register(Circle)
def draw_circle(c: Circle, x=0, y=0, col=None):
    pos = c.center_of_gravity
    pos = c.body.local_to_world((pos.x, pos.y))
    col = FOREGROUND_COLOR if col is None else col
    pyxel.circ(x + pos.x, y + pos.y, c.radius, col)


@draw.register(Segment)
def draw_segment(s: Segment, x=0, y=0, col=None):
    (x1, y1), (x2, y2) = map(s.body.local_to_world, [s.a, s.b])
    col = FOREGROUND_COLOR if col is None else col
    pyxel.line(x1 + x, y1 + y, x2 + x, y2 + y, col)


@draw.register(Poly)
def draw_poly(s: Poly, x=0, y=0, col=None):
    vertices = map(s.body.local_to_world, s.get_vertices())
    col = FOREGROUND_COLOR if col is None else col
    return draw_poly_vertices(col, x, y, *vertices)


def draw_poly_vertices(col, x, y, *vertices):
    n = len(vertices)
    if n == 1:
        x, y = vertices[0]
        pyxel.pset(x, y, col)
    elif n == 2:
        (x1, y1), (x2, y2) = vertices
        pyxel.line(x1, x2, y1, y2, col)
    else:
        (x1, y1), (x2, y2), (x3, y3), *rest = vertices
        pyxel.tri(x1 + x, y1 + y, x2 + x, y2 + y, x3 + x, y3 + y, col)
        if rest:
            draw_poly_vertices(col, x, y, (x1, y1), (x3, y3), *rest)

#
# drawb() function
#
@drawb.register(Space)
def drawb_space(s: Space, x=0, y=0, col=None):
    for a in s.shapes:
        drawb(a, x, y, col)


@drawb.register(Body)
def drawb_body(b: Body, x=0, y=0, col=None):
    for s in b.shapes:
        drawb(s, x, y, col)


@drawb.register(Circle)
def drawb_circle(c: Circle, x=0, y=0, col=None):
    pos = c.center_of_gravity
    pos = c.body.local_to_world((pos.x, pos.y))
    col = FOREGROUND_COLOR if col is None else col
    pyxel.circb(x + pos.x, y + pos.y, c.radius, col)


@drawb.register(Poly)
def drawb_poly(s: Poly, x=0, y=0, col=None):
    vertices = map(s.body.local_to_world, s.get_vertices())
    col = FOREGROUND_COLOR if col is None else col
    return drawb_poly_vertices(col, x, y, *vertices)


drawb.register(Segment, draw_segment)


def drawb_poly_vertices(col, x, y, *vertices):
    n = len(vertices)
    if n == 1:
        x, y = vertices[0]
        pyxel.pset(x, y, col)
    else:
        first = vertices[0]
        a, *rest = vertices
        for pt in rest:
            pyxel.line(*a, *pt, col)
            a = pt
        pyxel.line(*pt, *first, col)