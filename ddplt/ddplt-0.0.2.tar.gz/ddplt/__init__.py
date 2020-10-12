import pkg_resources

__version__ = pkg_resources.get_distribution('ddplt').version

from . import heatmaps, classification
