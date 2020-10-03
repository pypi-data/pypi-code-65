import ast
import sys
from math import isclose, sqrt
from typing import Callable, List, Tuple

import plotly.express as px
import pytest
from numpy import arange

from taperable_helix import Helix, HelixLocation

# Default abs_tol
absolute_tol: float = 1e-6
relative_tol: float = 1e-9

# Data directory string
data_dir_str = "tests/data/"

X: int = 0
Y: int = 1
Z: int = 2


def xDist_3d(
    linePt1: Tuple[float, float, float], linePt2: Tuple[float, float, float]
) -> float:
    xDist: float = linePt1[X] - linePt2[X]
    # print(f"xDist_3d:+- xDist={xDist}")
    return xDist


def yDist_3d(
    linePt1: Tuple[float, float, float], linePt2: Tuple[float, float, float]
) -> float:
    yDist: float = linePt1[Y] - linePt2[Y]
    # print(f"yDist_3d:+- yDist={yDist}")
    return yDist


def zDist_3d(
    linePt1: Tuple[float, float, float], linePt2: Tuple[float, float, float]
) -> float:
    zDist: float = linePt1[Z] - linePt2[Z]
    # print(f"zDist_3d:+- zDist={zDist}")
    return zDist


def dist_3d(
    linePt1: Tuple[float, float, float], linePt2: Tuple[float, float, float]
) -> float:
    dist: float = sqrt(
        pow(xDist_3d(linePt1, linePt2), 2)
        + pow(yDist_3d(linePt1, linePt2), 2)
        + pow(zDist_3d(linePt1, linePt2), 2)
    )
    # print(f"dist_2d:+- dist={dist}")
    return dist


def isclose_tuple(
    v1: Tuple[float, ...],
    v2: Tuple[float, ...],
    rel_tol: float = relative_tol,
    abs_tol: float = absolute_tol,
) -> bool:
    # print(f"isclose_tuple: v1={v1} v2={v2}")
    return all(
        [isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol) for a, b in zip(v1, v2)]
    )


def isclose_points(
    result: List[Tuple[float, float, float]],
    expected: List[Tuple[float, float, float]],
    rel_tol: float = relative_tol,
    abs_tol: float = absolute_tol,
) -> bool:
    # print(f"isclose_points: result={result} expected={expected}")
    return all([isclose_tuple(v1, v2) for v1, v2 in zip(result, expected)])


def generate_points(
    f: Callable[[float], Tuple[float, float, float]],
    first_t: float,
    last_t: float,
    inc: float,
) -> List[Tuple[float, float, float]]:
    pts: List[Tuple[float, float, float]] = list(map(f, arange(first_t, last_t, inc)))
    pts.append(f(last_t))
    # print(f"generate_points: len(pts)={len(pts)} first_t={first_t} last_t={last_t} pts={pts}")
    return pts


def write_points(fname: str, points: List[Tuple[float, float, float]]) -> None:
    with open(fname + ".txt", "w") as f:
        for x, y, z in points:
            f.writelines(f"{x}, {y}, {z},\n")


def read_points(fname: str) -> List[Tuple[float, float, float]]:
    points: List[Tuple[float, float, float]]
    with open(fname + ".txt", "r") as f:
        points = [ast.literal_eval(line) for line in f]
    return points


def print_points(prompt: str, points: List[Tuple[float, float, float]]) -> None:
    print(f"{prompt}: ", end="")
    for x, y, z in points:
        print(f"({x:.4f}, {y:.4f}, {z:.4f})", end=", ")
    print("")


def view(
    title: str,
    points: List[Tuple[float, float, float]],
    first_t: float,
    last_t: float,
    inc: float,
) -> None:
    # print(f"view: points={points}")
    fig = px.line_3d(
        title=title,
        x=[x for x, _, _ in points],
        y=[y for _, y, _ in points],
        z=[z for _, _, z in points],
    )
    fig.layout.scene.camera.projection.type = "orthographic"
    fig.show()


def doit(
    func_name: str,
    points: List[Tuple[float, float, float]],
    first_t: float,
    last_t: float,
    inc: float,
    viewable: bool = False,
    generate: bool = False,
) -> None:
    fname: str = data_dir_str + func_name
    if generate:
        write_points(fname, points)
    if viewable:
        view(func_name, points, first_t, last_t, inc)
    expected = read_points(fname)
    assert isclose_points(points, expected)


def test_helix(view, generate):
    func_name: str = sys._getframe().f_code.co_name
    inc = 0.1
    radius = 1
    pitch = 1
    height = 1
    h = Helix(radius=radius, pitch=pitch, height=height)
    f = h.helix()
    points = generate_points(f, h.first_t, h.last_t, inc)
    doit(
        func_name, points, h.first_t, h.last_t, inc, viewable=view, generate=generate,
    )

    # A "helix" with all points equidistant from z-axis by the raidus
    assert all(
        [
            isclose(
                dist_3d((0, 0, pt[Z]), pt),
                radius,
                rel_tol=relative_tol,
                abs_tol=absolute_tol,
            )
            for pt in points
        ]
    )


def test_helix_backwards(view, generate):
    func_name: str = sys._getframe().f_code.co_name
    inc = 0.1
    radius = 1
    pitch = 1
    height = 1
    h = Helix(radius=radius, pitch=pitch, height=height)
    f = h.helix()
    points = generate_points(f, h.first_t, h.last_t, inc)
    doit(
        func_name, points, h.first_t, h.last_t, inc, viewable=view, generate=generate,
    )

    # Validate the swapping of first_t and last_t creates the same helix
    h.first_t, h.last_t = h.last_t, h.first_t
    f = h.helix()
    # Generate the points, since we're starting at last_t we must use -inc
    # otherwise we'll only generate the last point
    points_backwards = generate_points(f, h.first_t, h.last_t, -inc)
    assert isclose_points(points, points_backwards)


def test_helix_torp_0pt1_tirp_0pt9_ho_0pt2(view, generate):
    func_name: str = sys._getframe().f_code.co_name
    inc = 0.05
    radius = 1
    pitch = 1
    height = 1
    torp = 0.1
    tirp = 0.9
    ho = 0.2
    h = Helix(
        radius=radius,
        pitch=pitch,
        height=height,
        taper_out_rpos=torp,
        taper_in_rpos=tirp,
    )
    f = h.helix(HelixLocation(horz_offset=ho))
    points = generate_points(f, h.first_t, h.last_t, inc)
    doit(
        func_name, points, h.first_t, h.last_t, inc, viewable=view, generate=generate,
    )

    # A "helix" with a convergence factor of 0.1. The distance from the center line
    # to the first and last points should be the radius.
    assert isclose_tuple((0, radius, 0), points[0])
    assert isclose_tuple((0, radius, height), points[-1])

    # The distance to the second point and the penultimate point are > radius
    assert dist_3d(points[1], (0, 0, points[1][Z])) > radius
    assert dist_3d(points[-2], (0, 0, points[-2][Z])) > radius

    # All other points should be equal to radius + ho
    assert all(
        [
            isclose(
                dist_3d((0, 0, pt[Z]), pt),
                radius + ho,
                rel_tol=relative_tol,
                abs_tol=absolute_tol,
            )
            for pt in points[2:-2]
        ]
    )


def test_helix_trp_validity(view, generate):
    radius = 1
    pitch = 1
    height = 1

    h = Helix(radius=radius, pitch=pitch, height=height,)

    h.taper_out_rpos = -0.1
    h.taper_in_rpos = 0.9
    with pytest.raises(ValueError):
        h.helix()

    h.taper_out_rpos = 1.00000000000001
    h.taper_in_rpos = 0.9
    with pytest.raises(ValueError):
        h.helix()

    h.taper_out_rpos = 0.1
    h.taper_in_rpos = -0.00000001
    with pytest.raises(ValueError):
        h.helix()

    h.taper_out_rpos = 0.1
    h.taper_in_rpos = 1.00000001
    with pytest.raises(ValueError):
        h.helix()

    h.taper_out_rpos = 0
    h.taper_in_rpos = 0.9
    h.helix()

    h.taper_out_rpos = 0.9
    h.taper_in_rpos = 1
    h.helix()

    h.taper_out_rpos = 0.1
    h.taper_in_rpos = 0.7
    h.helix()

    h.taper_out_rpos = 0.7
    h.taper_in_rpos = 0.8
    h.helix()

    h.taper_out_rpos = 0.1
    h.taper_in_rpos = 0.9
    h.helix()


def test_radius_0(view, generate):
    func_name: str = sys._getframe().f_code.co_name
    inc = 0.1
    h = Helix(radius=0, pitch=1, height=1)
    f = h.helix()
    points = generate_points(f, h.first_t, h.last_t, inc)
    doit(
        func_name, points, h.first_t, h.last_t, inc, viewable=view, generate=generate,
    )
    # A vertical line starting at 0 ending at 1
    first_pt = (0, 0, 0)
    last_pt = (0, 0, 1)
    assert points[0] == first_pt
    assert points[-1] == last_pt
    assert all(
        [
            (pt[0], pt[1], 0) == (0, 0, 0) and (pt >= first_pt) and (pt <= last_pt)
            for pt in points
        ]
    )


def test_radius_0_ft_0_lt_0(view, generate):
    func_name: str = sys._getframe().f_code.co_name
    inc = 0.1
    h = Helix(radius=0, pitch=1, height=1, first_t=0, last_t=0)
    f = h.helix()
    points = generate_points(f, h.first_t, h.last_t, inc)
    doit(
        func_name, points, h.first_t, h.last_t, inc, viewable=view, generate=generate,
    )

    # A point at origin
    assert len(points) == 1
    assert points[0] == (0, 0, 0)


def test_radius_0_ft_neg_1_lt_pos_1(view, generate):
    func_name: str = sys._getframe().f_code.co_name
    inc = 0.1
    h = Helix(radius=0, pitch=1, height=1, first_t=-1, last_t=1)
    f = h.helix()
    points = generate_points(f, h.first_t, h.last_t, inc)
    doit(
        func_name, points, h.first_t, h.last_t, inc, viewable=view, generate=generate,
    )
    # A vertical line starting at 0 ending at 1
    first_pt = (0, 0, 0)
    last_pt = (0, 0, 1)
    assert points[0] == first_pt
    assert points[-1] == last_pt
    assert all(
        [
            (pt[0], pt[1], 0) == (0, 0, 0) and (pt >= first_pt) and (pt <= last_pt)
            for pt in points
        ]
    )


def test_radius_0_ft_0_lt_neg_1(view, generate):
    func_name: str = sys._getframe().f_code.co_name
    inc = -0.1
    h = Helix(radius=0, pitch=1, height=1, first_t=0, last_t=-1)
    f = h.helix()
    points = generate_points(f, h.first_t, h.last_t, inc)
    doit(
        func_name, points, h.first_t, h.last_t, inc, viewable=view, generate=generate,
    )

    # A vertical line starting at 1 ending at 0
    first_pt = (0, 0, 0)
    last_pt = (0, 0, 1)
    assert points[0] == first_pt
    assert points[-1] == last_pt
    assert all(
        [
            (pt[0], pt[1], 0) == (0, 0, 0) and (pt >= first_pt) and (pt <= last_pt)
            for pt in points
        ]
    )


def test_radius_0_ft_neg_2_lt_neg_1(view, generate):
    func_name: str = sys._getframe().f_code.co_name
    inc = 0.1
    h = Helix(radius=0, pitch=1, height=1, first_t=-2, last_t=-1)
    f = h.helix()
    points = generate_points(f, h.first_t, h.last_t, inc)
    doit(
        func_name, points, h.first_t, h.last_t, inc, viewable=view, generate=generate,
    )

    # A vertical line starting at 1 ending at 0
    first_pt = (0, 0, 0)
    last_pt = (0, 0, 1)
    assert points[0] == first_pt
    assert points[-1] == last_pt
    assert all(
        [
            (pt[0], pt[1], 0) == (0, 0, 0) and (pt >= first_pt) and (pt <= last_pt)
            for pt in points
        ]
    )


def test_radius_0_ft_neg_1_lt_neg_2(view, generate):
    func_name: str = sys._getframe().f_code.co_name
    inc = -0.1
    h = Helix(radius=0, pitch=1, height=1, first_t=-1, last_t=-2)
    f = h.helix()
    points = generate_points(f, h.first_t, h.last_t, inc)
    doit(
        func_name, points, h.first_t, h.last_t, inc, viewable=view, generate=generate,
    )

    # A vertical line starting at 0 ending at 1
    first_pt = (0, 0, 0)
    last_pt = (0, 0, 1)
    assert points[0] == first_pt
    assert points[-1] == last_pt
    assert all(
        [
            (pt[0], pt[1], 0) == (0, 0, 0) and (pt >= first_pt) and (pt <= last_pt)
            for pt in points
        ]
    )


def test_radius_0_height_0(view, generate):
    func_name: str = sys._getframe().f_code.co_name
    inc = 0.1
    h = Helix(radius=0, pitch=1, height=0)
    f = h.helix()
    points = generate_points(f, h.first_t, h.last_t, inc)
    doit(
        func_name, points, h.first_t, h.last_t, inc, viewable=view, generate=generate,
    )

    # All points at origin (0, 0, 0)
    assert all([(pt == (0, 0, 0)) for pt in points])


def test_radius_0_height_neg_1(view, generate):
    func_name: str = sys._getframe().f_code.co_name
    inc = 0.1
    h = Helix(radius=0, pitch=1, height=-1)
    f = h.helix()
    points = generate_points(f, h.first_t, h.last_t, inc)
    doit(
        func_name, points, h.first_t, h.last_t, inc, viewable=view, generate=generate,
    )

    # A vertical line starting at 0 ending at -1
    first_pt = (0, 0, 0)
    last_pt = (0, 0, -1)
    assert points[0] == first_pt
    assert points[-1] == last_pt
    assert all(
        [
            (pt[0], pt[1], 0) == (0, 0, 0) and (pt <= first_pt) and (pt >= last_pt)
            for pt in points
        ]
    )


def test_radius_0_ft_pos_0_lt_neg_1_height_neg_1(view, generate):
    func_name: str = sys._getframe().f_code.co_name
    inc = -0.1
    h = Helix(radius=0, pitch=1, height=-1, first_t=0, last_t=-1)
    f = h.helix()
    points = generate_points(f, h.first_t, h.last_t, inc)
    doit(
        func_name, points, h.first_t, h.last_t, inc, viewable=view, generate=generate,
    )

    # A vertical line starting at 0 ending at -1
    first_pt = (0, 0, 0)
    last_pt = (0, 0, -1)
    assert points[0] == first_pt
    assert points[-1] == last_pt
    assert all(
        [
            (pt[0], pt[1], 0) == (0, 0, 0) and (pt <= first_pt) and (pt >= last_pt)
            for pt in points
        ]
    )


def test_radius_0_io_0pt1(view, generate):
    func_name: str = sys._getframe().f_code.co_name
    inc = 0.1
    inset = 0.1
    h = Helix(radius=0, pitch=1, height=1, inset_offset=inset,)
    f = h.helix()
    points = generate_points(f, h.first_t, h.last_t, inc)
    doit(
        func_name, points, h.first_t, h.last_t, inc, viewable=view, generate=generate,
    )

    # A vertical line starting at 0.1 ending at 0.9
    first_pt = (0, 0, inset)
    last_pt = (0, 0, 1 - inset)
    assert points[0] == first_pt
    assert points[-1] == last_pt
    assert all(
        [
            (pt[0], pt[1], 0) == (0, 0, 0) and (pt >= first_pt) and (pt <= last_pt)
            for pt in points
        ]
    )


def test_radius_0_ft_0_lt_0_io_neg_0pt1(view, generate):
    func_name: str = sys._getframe().f_code.co_name
    first_t = 0
    last_t = 0
    inc = 0.1
    inset = -0.1
    h = Helix(
        radius=0, pitch=1, height=1, inset_offset=inset, first_t=first_t, last_t=last_t
    )
    f = h.helix()
    points = generate_points(f, h.first_t, h.last_t, inc)
    doit(
        func_name, points, first_t, last_t, inc, viewable=view, generate=generate,
    )

    # A point at origin (0, 0, inset)
    assert len(points) == 1
    assert points[0] == (0, 0, inset)


def test_pitch_0_height_0(view, generate):
    func_name: str = sys._getframe().f_code.co_name
    inc = 0.1
    radius = 1
    height = 0
    h = Helix(radius=radius, pitch=0, height=height)
    f = h.helix()
    points = generate_points(f, h.first_t, h.last_t, inc)
    doit(
        func_name, points, h.first_t, h.last_t, inc, viewable=view, generate=generate,
    )

    # A "circle" centered around the origin
    origin = (0, 0, 0)
    center = (0, 0, height)
    assert center == origin
    assert all(
        [
            (pt[Z] == height)
            and isclose(
                dist_3d(center, pt), radius, rel_tol=relative_tol, abs_tol=absolute_tol
            )
            for pt in points
        ]
    )


def test_pitch_0_height_1(view, generate):
    func_name: str = sys._getframe().f_code.co_name
    inc = 0.1
    radius = 1
    height = 1
    h = Helix(radius=radius, pitch=0, height=height)
    f = h.helix()
    points = generate_points(f, h.first_t, h.last_t, inc)
    doit(
        func_name, points, h.first_t, h.last_t, inc, viewable=view, generate=generate,
    )

    # A "circle" centered around the height
    center = (0, 0, height)
    assert all(
        [
            (pt[Z] == height)
            and isclose(
                dist_3d(center, pt), radius, rel_tol=relative_tol, abs_tol=absolute_tol
            )
            for pt in points
        ]
    )


def test_pitch_0_ho_1(view, generate):
    func_name: str = sys._getframe().f_code.co_name
    inc = 0.1
    radius = 1
    ho = 1
    h = Helix(radius=radius, pitch=0, height=0)
    f = h.helix(HelixLocation(horz_offset=ho))
    points = generate_points(f, h.first_t, h.last_t, inc)
    doit(
        func_name, points, h.first_t, h.last_t, inc, viewable=view, generate=generate,
    )

    # A "circle" centered at 0 with a radius = radius + ho
    center = (0, 0, 0)
    assert all(
        [
            (pt[Z] == 0)
            and isclose(
                dist_3d(center, pt),
                radius + ho,
                rel_tol=relative_tol,
                abs_tol=absolute_tol,
            )
            for pt in points
        ]
    )


def test_pitch_0_vo_1(view, generate):
    func_name: str = sys._getframe().f_code.co_name
    inc = 0.1
    radius = 1
    vo = 1
    h = Helix(radius=radius, pitch=0, height=0)
    f = h.helix(HelixLocation(vert_offset=vo))
    points = generate_points(f, h.first_t, h.last_t, inc)
    doit(
        func_name, points, h.first_t, h.last_t, inc, viewable=view, generate=generate,
    )

    # A "circle" centered around the horz_offset
    center = (0, 0, vo)
    assert all(
        [
            (pt[Z] == vo)
            and isclose(
                dist_3d(center, pt), radius, rel_tol=relative_tol, abs_tol=absolute_tol
            )
            for pt in points
        ]
    )
