import os
from sys import path

from anyscale.report import report

__version__ = "0.3.4"

__all__ = ["report"]

anyscale_dir = os.path.dirname(os.path.abspath(__file__))
path.append(os.path.join(anyscale_dir, "client"))
path.insert(0, os.path.join(anyscale_dir, "anyscale_ray"))
