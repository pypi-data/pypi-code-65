"""Top-level package for Spatial Semantic Pointers."""

__author__ = """Nicole Sandra-Yaffa Dumont"""
__email__ = 'nicole.s.dumont@gmail.com'
__version__ = '0.1.0'

import nengo_ssp.dists
import nengo_ssp.hrr_algebra
import nengo_ssp.plotting
import nengo.ssp_networks
from nengo_ssp.spatial_semantic_pointer import SpatialSemanticPointer
import nengo_ssp.utils
from nengo_ssp.vector_generation import (
    PlaneWaveBasis,
    WeightedPlaneWaveBasis,
    HexagonalBasis,
    RecursiveBasisFun,
    GridCellEncoders,
    UnitaryVectors
)
