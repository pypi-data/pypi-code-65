from typing import Tuple
from geopy.distance import geodesic, Distance

from .location import Location

try:
    from geo.ellipsoid import distance
except ImportError:
    ellipsoid_distance = None
else:

    # NOTE: I have to adher to this interface so as not to break the
    # package. The geopy lib authors have decided to couple Distance
    # calculation and the distance type together
    class ellipsoid_distance(Distance):
        def measure(self, a: Tuple[float, float], b: Tuple[float, float]) -> float:
            return distance(a, b) / 1000


def geodesic_location_distance(l1: Location, l2: Location) -> Distance:
    """
    This uses a pure python library to compute distance between l1 and l2.
    """
    loc1 = (l1.lat, l1.lng)
    loc2 = (l2.lat, l2.lng)
    return geodesic(loc1, loc2)


def approx_location_distance(l1: Location, l2: Location) -> Distance:
    """
    This uses a C library under the hood to compute distance between l1 and l2.
    Caveats:
    1. You have to install it yourself
    2. It is unmaintained
    3. Builds from source/Does not have a many_linux wheel
    """
    if not ellipsoid_distance:
        raise RuntimeError("Install geo-py for this version to work")

    loc1 = (l1.lat, l1.lng)
    loc2 = (l2.lat, l2.lng)

    return ellipsoid_distance(loc1, loc2)
