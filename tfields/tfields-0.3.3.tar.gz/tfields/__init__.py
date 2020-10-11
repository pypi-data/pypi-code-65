"""Top-level package of tfields."""

__author__ = """Daniel Böckenhoff"""
__email__ = "dboe@ipp.mpg.de"
__version__ = "0.3.3"

# methods:
from tfields.core import dim, rank  # NOQA
from tfields.mask import evalf  # NOQA

# classes:
from tfields.core import Tensors, TensorFields, TensorMaps, Container, Maps  # NOQA
from tfields.points3D import Points3D  # NOQA
from tfields.mesh3D import Mesh3D  # NOQA
from tfields.triangles3D import Triangles3D  # NOQA
from tfields.planes3D import Planes3D  # NOQA
from tfields.bounding_box import Node  # NOQA
