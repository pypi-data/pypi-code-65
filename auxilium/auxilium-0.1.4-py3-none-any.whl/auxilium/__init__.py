# -*- coding: utf-8 -*-

# auxilium
# --------
# A Python project for an automated test and deploy toolkit - 100%
# reusable.
# 
# Author:   sonntagsgesicht
# Version:  0.1.4, copyright Sunday, 11 October 2020
# Website:  https://github.com/sonntagsgesicht/auxilium
# License:  Apache License 2.0 (see LICENSE file)


__doc__ = 'A Python project for an automated test and deploy toolkit - 100% reusable.'
__version__ = '0.1.4'
__dev_status__ = '3 - Alpha'
__date__ = 'Sunday, 11 October 2020'
__author__ = 'sonntagsgesicht'
__email__ = __author__ + '@icloud.com'
__url__ = 'https://github.com/' + __author__ + '/' + __name__
__license__ = 'Apache License 2.0'
__dependencies__ = 'pylint', 'coverage', 'bandit', 'twine', 'sphinx', 'sphinx_rtd_theme', 'flake8', 'codecov', 'requests'
__dependency_links__ = ()
__data__ = ('data/pkg.zip',)
__scripts__ = ('auxilium/scripts/auxilium', 'auxilium/scripts/multum-auxilium')

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

from .rst_tools import replacements_str, replacements_from_pkg, replacements_from_cls, replacements

from .tools.setup_tools import *
from .tools.test_tools import *
from .tools.documentation_tools import *
from .tools.deployment_tools import *
