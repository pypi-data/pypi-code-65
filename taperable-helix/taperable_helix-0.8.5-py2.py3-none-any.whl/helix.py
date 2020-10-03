from dataclasses import dataclass
from math import cos, degrees, pi, sin
from typing import Callable, Optional, Tuple


@dataclass
class HelixLocation:
    radius: Optional[float] = None  #: radius of helix if none h.radius
    horz_offset: float = 0  #: horizontal offset  added to radius then x and y calculated
    vert_offset: float = 0  #: vertical added to z of radius


@dataclass
class Helix:
    """This class represents a taperable Helix.

    The required attributes are radius,
    pitch and height. Thse attributes create simple single line helix.
    But the primary purpose for Helix is to create a set of helical "wires"
    using non-zero values for taper_rpos, horz_offset and vert_offset to
    define solid helixes that can taper at each end to a point.

    This is useful for creating internal and external threads for nuts and
    bolts.  This is accomplished by invoking helix() multiple times with
    same radius, pitch, taper_rpos, inset_offset, first_t, and last_t.
    But with different HelixLocation radius, horz_offset and vert_offset.

    Each returned function will then generate a helix defining an edge
    of the thread. The edges can be used to make faces and subsequently
    a solid of the thread. This can then be combined with the "core" objects
    which the threads are "attached" using a "union" operator.
    """

    radius: float #: radius of the basic helix.

    pitch: float
    """pitch of the helix per revolution. I.e the distance between the
    height of a single "turn" of the helix.
    """

    height: float  #: height of the cyclinder containing the helix.

    taper_out_rpos: float = 0
    """taper_out_rpos is a decimal number with an inclusive range of 0..1
    such that (taper_out_rpos * t_range) defines the t value where tapering
    out ends, it begins at t == first_t.  A ValueError exception is raised
    if taper_out_rpos < 0 or > 1 or taper_out_rpos > taper_in_rpos.
    Default is 0 which is no out taper.
    """

    taper_in_rpos: float = 1
    """taper_in_rpos: is a decimal number with an inclusive range of 0..1
    such that (taper_in_rpos * t_range) defines the t value where tapering
    in begins, it ends at t == last_t.  A ValueError exception is raised
    if taper_out_rpos < 0 or > 1 or taper_out_rpos > taper_in_rpos.
    Default is 1 which is no in taper.
    """

    inset_offset: float = 0
    """inset_offset: the helix will start at z = inset_offset and will
    end at z = height - (2 * inset_offset). Default 0.
    """

    first_t: float = 0  #: first_t is the first t value passed to the returned function. Default 0

    last_t: float = 1 #: last_t is the last t value passed to the returned function. Default 1


    def helix(
        self, hl: Optional[HelixLocation] = None
    ) -> Callable[[float], Tuple[float, float, float]]:
        """This function returns a Function that is used to generates points
        on a helix.

        It takes an optional HelixLocation which refines the location of the
        final helix when its tapered. If HelixLocation is None then the radius
        is Helix.radius and horz_offset and vert_offset will be 0. If its not None
        HelixLocation.radius maybe None, in which case Helix.radius will be used.
        and HelixLocation.horz_offset will be added to the radius and used to
        calculate x and y. The HelixLocation.vert_offset will be added to z.

        This function returns a function, f. The funciton f that takes one parameter,
        an inclusive value between first_t and last_t.  We then define
        t_range=last_t-first_t and the rel_height=(last_t-t)/t_range. The rel_height
        is the relative position along the "z-axis" which is used to calculate function
        functions returned tuple(x, y, z) for a point on the helix.

        Credit: Adam Urbanczyk from cadquery [forum post](https://groups.google.com/g/cadquery/c/5kVRpECcxAU/m/7no7_ja6AAAJ)

        :param hl: Defines a refinded location when the helix is tapered
        :returns: A function which is passed "t", an inclusive value between first_t
                  and last_t and returns a 3D point (x, y, z) on the helix as a
                  function of t.
        """
        if self.taper_out_rpos > self.taper_in_rpos:
            raise ValueError(
                f"taper_out_rpos:{self.taper_out_rpos} > taper_in_rpos:{self.taper_in_rpos}"
            )

        if self.taper_out_rpos < 0 or self.taper_out_rpos > 1:
            raise ValueError(
                f"taper_out_rpos:{self.taper_out_rpos} should be >= 0 and <= 1"
            )

        if self.taper_in_rpos < 0 or self.taper_in_rpos > 1:
            raise ValueError(
                f"taper_in_rpos:{self.taper_in_rpos} should be >= 0 and <= 1"
            )

        # Being "Tricky" to be flexible
        if hl is None:
            hl = HelixLocation(self.radius)
        elif hl.radius is None:
            hl.radius = self.radius

        # Reduce the height by 2 * inset_offset. Threads start at inset_offset
        # and end at height - inset_offset
        helix_height: float = (self.height - (2 * self.inset_offset))

        # The number or revolutions of the helix within the helix_height
        # set to 1 if pitch or helix_height is 0
        turns: float = self.pitch / helix_height if self.pitch != 0 and helix_height != 0 else 1

        # With this DISABLED points t_range will be negative
        # when self.last_t < self.first_t. This causes rel_height in "f"
        # to be negative and as a consequence # the values
        # generated by "f" will always be the same order.
        # See test_helix_backwards.
        #
        # If we ENABLE the code below and swap the order
        # if self.last_t < self.first_t then test_helix_backwards will
        # fail because the order of points in the resulting
        # array will be in reversed order.
        #
        # if self.last_t < self.first_t:
        #     self.last_t, self.first_t = self.first_t, self.last_t

        t_range: float = self.last_t - self.first_t

        taper_out_range: float = t_range * self.taper_out_rpos
        taper_out_ends: float = self.first_t + taper_out_range if taper_out_range > 0 else min(
            self.first_t, self.last_t
        )

        taper_in_range: float = t_range * (1 - self.taper_in_rpos)
        taper_in_starts: float = self.last_t - taper_in_range if taper_in_range > 0 else max(
            self.first_t, self.last_t
        )

        # print(f"helix: ft={self.first_t:.4f} lt={self.last_t:.4f} tr={t_range:.4f}")
        # print(f"helix: tor={taper_out_range:.4f} toe={taper_out_ends:.4f}")
        # print(f"helix: tir={taper_in_range:.4f} tis={taper_in_starts:.4f}")

        def func(t: float) -> Tuple[float, float, float]:
            """
            Return a tuple(x, y, z)
            :param t: A value between self.first_t .. self.last_t inclusive
            """

            # This if statement is needed to satisfy mypy this is already
            # guaranteed in helix() above.
            if (hl is None) or (hl.radius is None):
                raise ValueError("hl or hl.radius is None, should never happen")

            taper_angle: float
            toffset: float = t - self.first_t
            rel_height: float = toffset / t_range if t_range != 0 else 0

            # print(f"f:  t={t:.4f}")
            # print(f"f:  tor={taper_out_range:.4f} toe={taper_out_ends:.4f}")
            # print(f"f:  tir={taper_in_range:.4f} tis={taper_in_starts:.4f}")
            if t < taper_out_ends:
                # Taper out from a point, taper_scale will be between 0 and 1
                # This code path is used when t < taper_out and this helix
                # will smoothly taper from a point as taper angle starts at 0
                # and increases to p/2.
                # print(f"f:  out t={t:.4f} < taper_out_ends:{taper_out_ends}")
                taper_angle = pi / 2 * (t - self.first_t) / taper_out_range
            elif t <= taper_in_starts:
                # No tapering, taper_scale == 1
                # print(f"f:  no  t={t:.4f} >= taper_out_ends:{taper_out_ends} <= taper_in_starts:{taper_in_starts}")
                taper_angle = pi / 2
            else:
                # This code path is used when t > taper_in_starts and the this helix
                # will smoothly taper to a point as taper angle starts at p/2
                # and decrease to 0.
                # print(f"f:  in  t={t:.4f} > taper_in_starts:{taper_in_starts}")
                taper_angle = pi / 2 * (self.last_t - t) / taper_in_range

            # print(f"taper_angle={taper_angle}")
            taper_scale: float = sin(taper_angle)

            r: float = hl.radius + (hl.horz_offset * taper_scale)
            a: float = (2 * pi / turns) * rel_height

            x: float = r * sin(-a)
            y: float = r * cos(a)
            z: float = (
                (helix_height * (rel_height if self.pitch != 0 else 1))
                + (hl.vert_offset * taper_scale)
                + self.inset_offset
            )

            result: Tuple[float, float, float] = (x, y, z)
            # print(f"f:  tpa={degrees(taper_angle):.4f} tps={taper_scale:.4f} r={r:.4f} a={degrees(a):.4f}")
            # print(f"f:  t={t:.4f} toffset={toffset:.4f} rh={rel_height:.4f} result={result}")
            return result

        return func
