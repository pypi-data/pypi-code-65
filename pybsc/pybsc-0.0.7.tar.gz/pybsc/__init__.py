# flake8: noqa

import pkg_resources


__version__ = pkg_resources.get_distribution("pybsc").version


from pybsc.split import nsplit

from pybsc.iter_utils import pairwise
from pybsc.iter_utils import triplewise

from pybsc.json_utils import load_json
from pybsc.json_utils import save_json
