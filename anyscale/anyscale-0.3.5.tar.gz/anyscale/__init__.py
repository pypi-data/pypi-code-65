import os
from sys import path

from anyscale.report import report

__version__ = os.getenv("ANYSCALE_CLI_VERSION", "0.3.5")

__all__ = ["report"]

anyscale_dir = os.path.dirname(os.path.abspath(__file__))
path.append(os.path.join(anyscale_dir, "client"))
anyscale_ray_dir = os.path.join(anyscale_dir, "anyscale_ray")
path.insert(0, anyscale_ray_dir)

ANYSCALE_ENV = os.environ.copy()
ANYSCALE_ENV["PYTHONPATH"] = anyscale_ray_dir + ":" + ANYSCALE_ENV.get("PYTHONPATH", "")
