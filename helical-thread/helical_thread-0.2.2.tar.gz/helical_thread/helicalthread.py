from copy import deepcopy
from dataclasses import dataclass, field
from math import degrees, radians, sin, tan
from typing import List

from taperable_helix import Helix, HelixLocation


@dataclass
class HelicalThread(Helix):
    """
    A set of fields used to represent a helical thread and passed as
    the parameter to `helical_thread`.

    Control of the size and spacing of the thread using the various
    fields in Helix and those below.
    """

    angle_degs: float = 45
    """angle in degrees"""

    major_cutoff: float = 0
    """Size of of flat at the major diameter"""

    minor_cutoff: float = 0
    """Size of flat at the minor diameter"""

    ext_clearance: float = 0.1
    """External clearance between external and internal threads"""

    thread_overlap: float = 0.001
    """
    Amount to overlap threads with the core so the union of core and
    threads is a manifold
    """


@dataclass
class ThreadHelixes:
    """
    The helixes returned by helical_thread` that represents the internal
    thread, prefixed with `int_` and the external thread, prefixed with `ext_`.
    """

    ht: HelicalThread
    """The basic Dimensions of the helixes"""

    int_helix_radius: float = 0
    """The internal thread radius"""

    int_helixes: List[HelixLocation] = field(default_factory=list)
    """List of the internal helix locations"""

    ext_helix_radius: float = 0
    """The external thread radius"""

    ext_helixes: List[HelixLocation] = field(default_factory=list)
    """List of the external helix locations"""


def helical_thread(ht: HelicalThread) -> ThreadHelixes:
    """
    Given HelicalThread compute the internal and external
    helixes thread and returning them in ThreadHelixes.
    int_hexlix_radius, int_helixes, ext_helix_radius and ext_helixes.
    The helixes are an array of HelixLocations that define the helixes of
    the thread. If minor_cutoff is 0 then the thread will be triangular
    and the length of the {int|ext}_helixes 3. if minor_cutoff > 0 then
    the thread will be a trapezoid with the length of the {int|ext}_helixes
    will be 4.

    :param ht: The basic dimensions of the helicla thread
    :returns: internal and external helixes necessary to use taperable-helix
    """
    # print(
    #     f"helical_thread:+ height={height:.3f} pitch={pitch:.3f} angle_degs={angle_degs:.3f}"
    # )
    # print(
    #     f"helical_thread: inset={inset:.3f} ext_clearance={ext_clearance} taper_rpos={taper_rpos:.3f}"
    # )
    # print(
    #     f"helical_thread: major_cutoff={major_cutoff} minor_cutoff={minor_cutoff} thread_overlap={thread_overlap:.3f} "
    # )
    # print(
    #     f"helical_thread: first_t={first_t} last_t={last_t} "
    # )

    result: ThreadHelixes = ThreadHelixes(ht)

    angle_radians: float = radians(ht.angle_degs)
    tan_hangle: float = tan(angle_radians / 2)
    sin_hangle: float = sin(angle_radians / 2)
    tip_to_major_cutoff: float = ((ht.pitch - ht.major_cutoff) / 2) / tan_hangle
    tip_to_minor_cutoff: float = (ht.minor_cutoff / 2) / tan_hangle
    # print(
    #     f"helical_thread: tip_to_major_cutoff={tip_to_major_cutoff:.3f} tip_to_minor_cutoff={tip_to_minor_cutoff:.3f}"
    # )
    int_thread_depth: float = tip_to_major_cutoff - tip_to_minor_cutoff
    # print(f"helical_thread: int_thread_depth={int_thread_depth}")

    thread_overlap_vert_adj: float = ht.thread_overlap * tan_hangle
    thread_half_height_at_helix_radius: float = (
        (ht.pitch - ht.major_cutoff) / 2
    ) + thread_overlap_vert_adj
    thread_half_height_at_opposite_helix_radius: float = ht.minor_cutoff / 2
    # print(
    #     f"thh_at_r={thread_half_height_at_helix_radius} thh_at_or={thread_half_height_at_opposite_helix_radius} td={int_thread_depth}"
    # )

    # Internal thread have helix thread radisu
    result.int_helix_radius = ht.radius
    result.int_helixes = []

    # print(f"result.int_helix_radius={result.int_helix_radius}")
    hl = HelixLocation(
        radius=result.int_helix_radius + ht.thread_overlap,
        horz_offset=0,
        vert_offset=-thread_half_height_at_helix_radius,
    )
    result.int_helixes.append(hl)

    hl = HelixLocation(
        radius=result.int_helix_radius + ht.thread_overlap,
        horz_offset=0,
        vert_offset=+thread_half_height_at_helix_radius,
    )
    result.int_helixes.append(hl)

    hl = HelixLocation(
        radius=result.int_helix_radius,
        horz_offset=-int_thread_depth,
        vert_offset=+thread_half_height_at_opposite_helix_radius,
    )
    result.int_helixes.append(hl)

    if ht.minor_cutoff > 0:
        hl = HelixLocation(
            radius=result.int_helix_radius,
            horz_offset=-int_thread_depth,
            vert_offset=-thread_half_height_at_opposite_helix_radius,
        )
        result.int_helixes.append(hl)

    # Use ext_clearance to calcuate external thread values

    # hyp is the hypothense of the trinagle formed by a radial
    # line, the tip of the internal thread and the tip of the
    # external thread.
    hyp: float = ht.ext_clearance / sin_hangle

    # ext_vert_adj is the amount to ajdust verticaly the helix
    ext_vert_adj: float = (hyp - ht.ext_clearance) * tan_hangle
    # print(f"hyp={hyp} ext_vert_adj={ext_vert_adj}")

    # External thread have the helix on the minor side and
    # so we subtract the int_thread_depth and ext_clearance from ht.radius
    result.ext_helix_radius = ht.radius - int_thread_depth - ht.ext_clearance
    # print(
    #     f"result.ext_helix_radius={ht.ext_helix_radius} td={int_thread_depth} ec={ht.ext_clearance}"
    # )

    ext_thread_half_height_at_ext_helix_radius: float = (
        (ht.pitch - ht.minor_cutoff) / 2
    ) - ext_vert_adj
    ext_thread_half_height_at_ext_helix_radius_plus_tova: float = (
        ext_thread_half_height_at_ext_helix_radius + thread_overlap_vert_adj
    )

    # When major cutoff becomes smaller than the exter_vert_adj then the
    # external thread will only be three points and we set
    # ext_thrad_half_height_at_opposite_ext_helix_radius # to 0 and
    # compute the thread depth. Under these circumstances the clearance
    # from the external tip to internal core will be close to ext_clearance
    # or greater. See test_thread.py or test_thread_new.py.
    ext_thread_half_height_at_opposite_ext_helix_radius: float = (
        ht.major_cutoff / 2
    ) - ext_vert_adj
    ext_thread_depth: float = int_thread_depth
    if ext_thread_half_height_at_opposite_ext_helix_radius < 0:
        ext_thread_half_height_at_opposite_ext_helix_radius = 0
        ext_thread_depth = ext_thread_half_height_at_ext_helix_radius / tan_hangle

    # print(
    #     f"ext_thread_depth={ext_thread_depth} ext_thh_at_ehr={ext_thread_half_height_at_ext_helix_radius} ext_thh_at_ehr_plus_tovo={ext_thread_half_height_at_ext_helix_radius_plus_tova} ext_thh_at_oehr={ext_thread_half_height_at_opposite_ext_helix_radius}"
    # )

    result.ext_helixes = []
    hl = HelixLocation(
        radius=result.ext_helix_radius - ht.thread_overlap,
        horz_offset=0,
        vert_offset=-ext_thread_half_height_at_ext_helix_radius_plus_tova,
    )
    result.ext_helixes.append(hl)

    hl = HelixLocation(
        radius=result.ext_helix_radius - ht.thread_overlap,
        horz_offset=0,
        vert_offset=+ext_thread_half_height_at_ext_helix_radius_plus_tova,
    )
    result.ext_helixes.append(hl)

    hl = HelixLocation(
        radius=result.ext_helix_radius,
        horz_offset=ext_thread_depth,
        vert_offset=+ext_thread_half_height_at_opposite_ext_helix_radius,
    )
    result.ext_helixes.append(hl)

    if ext_thread_half_height_at_opposite_ext_helix_radius > 0:
        hl = HelixLocation(
            radius=result.ext_helix_radius,
            horz_offset=ext_thread_depth,
            vert_offset=-ext_thread_half_height_at_opposite_ext_helix_radius,
        )
        result.ext_helixes.append(hl)

    return result
