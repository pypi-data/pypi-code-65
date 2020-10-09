"""
Module for scoring how well interactions
perform w.r.t. some output.

In the more abstract sense, this means comparing
random variables in several statistics, firstly
via the mutual information statistic and
in linear regression models.
"""

from ._mutual import calculate_mi
from ._linear import calculate_pc, MultiVariateLinear
from ._ranking import feature_importance
