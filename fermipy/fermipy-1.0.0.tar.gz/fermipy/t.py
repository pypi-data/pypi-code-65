

from fermipy import gtanalysis
from os import path
cfgfile = path.join('fermipy_test_draco', 'config.yaml')
gta = gtanalysis.GTAnalysis(str(cfgfile))
gta.setup()
