import sys
from functools import partial

from .atomics.prep import Prep
from .atomics.meas import Meas
from .atomics.pres import Pres
from .atomics.gate import Gate
from .atomics.util import Util
from .atomics.test import Test

import logging

from qpz_atomics import __version__

__author__ = "Harold Ollivier"
__copyright__ = "Harold Ollivier"
__license__ = "mit"

_logger = logging.getLogger(__name__)

def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")

class lib:
    def __init__(self, backend_mapping, node):
        self.X = backend_mapping["X"]
        self.Y = backend_mapping["Y"]
        self.Z = backend_mapping["Z"]
        self.H = backend_mapping["H"]
        self.CNOT = backend_mapping["CNOT"]

        self.K = backend_mapping["K"]
        self.T = backend_mapping["T"]
        self.Tinv = backend_mapping["Tinv"]

        self.PREP = partial (backend_mapping["PREP"], node=node)
        self.MEAS = backend_mapping["MEAS"]
        self.DISP = backend_mapping["DISP"]
        self.QID = backend_mapping["QID"]

        self.EPR = backend_mapping["EPR"]
        self.SEND = partial (backend_mapping["SEND"], node=node)
        self.RECV = partial (backend_mapping["RECV"], node=node)
        self.TELE = backend_mapping["TELE"]

        mapp = self 
                        
        self.gate = Gate(mapp)
        self.prep = Prep(mapp)
        self.meas = Meas(mapp)
        self.pres = Pres(mapp)
        self.util = Util(mapp)
        self.test = Test(mapp)
        
        # def check():
        #     reqs = {
        #         "qotp": ['X', 'Y', 'Z'],
        #     }

        #     for f in reqs:
        #         availability= True
        #         for g in reqs[f]:
        #             if not(hasattr(self,g)) or (backend_mapping[g] is None): availability = False
        #         if availability:
        #             print(f"""Quantum Protocol Zoo Lib: {f} is available""")
        #         else:
        #             print(f"""Quantum Protocol Zoo Lib: {f} is unavailable""")
        #             setattr(self, f, self.raiseException)

        # check()

    def raiseException(*args, **kwargs):
        raise NameError(f"""Quantum Protocol Zoo Lib function is unavailable because the backend does not provide a necessary functionality""")



