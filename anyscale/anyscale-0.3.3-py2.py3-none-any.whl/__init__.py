import os
from sys import path

from anyscale.api import report

__version__ = "0.3.3"

__all__ = ["report"]

anyscale_dir = os.path.dirname(os.path.abspath(__file__))
path.append(os.path.join(anyscale_dir, "client"))
