import logging

import convo
from convo.nlu.train import train
from convo.nlu.test import run_evaluation as test
from convo.nlu.test import cross_validate

logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = convo.__version__
