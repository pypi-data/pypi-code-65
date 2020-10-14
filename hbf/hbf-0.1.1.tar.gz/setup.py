# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hbf', 'hbf.helpers', 'hbf.rescrape', 'hbf.tests']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.9.3,<5.0.0',
 'configparser>=5.0.0,<6.0.0',
 'geopy>=2.0.0,<3.0.0',
 'pandas>=1.1.3,<2.0.0',
 'progress>=1.5,<2.0',
 'requests>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'hbf',
    'version': '0.1.1',
    'description': "A program to predict a home's sell price using data scraped from the internet",
    'long_description': "# homeBuyerFire\n[![Build Status](https://travis-ci.com/MattThomas9/Home-Buyer-Fire.svg?branch=master)](https://travis-ci.com/MattThomas9/Home-Buyer-Fire)\n[![Actions Status](https://github.com/MattThomas9/Home-Buyer-Fire/workflows/Lint/badge.svg)](https://github.com/MattThomas9/Home-Buyer-Fire/actions)\n[![codecov](https://codecov.io/gh/MattThomas9/Home-Buyer-Fire/branch/master/graph/badge.svg?token=5AJUA8I31G)](https://codecov.io/gh/MattThomas9/Home-Buyer-Fire/)\n[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FMattThomas9%2FHome-Buyer-Fire.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2FMattThomas9%2FHome-Buyer-Fire?ref=badge_shield)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n## Project Overview\n\nA program to predict a home's sell price using data scraped from the internet.\n\n`homeBuyerFire` is actively developed using a Python 3.7 interpreter.\n\n## Installation\n\n```\npip install hbf\n```\n\n## Example\n\nStarting from the project's parent directory:\n\n```\npython example.py\n```\n\n```\nScraping Zillow |████████████████████████████████| 7/7\n\n                                       Address  Sell Price  Beds  Baths  Home Size      Home Type  Year Built                         Heating  Cooling Parking  Lot Size\n0  11705 College View Dr Silver Spring MD 20902    293000.0   2.0    2.0     1526.0  Single Family      1951.0                      Forced air  Central     NaN    6791.0\n1  11714 College View Dr Silver Spring MD 20902    465000.0   4.0    3.0     2843.0  Single Family      1962.0  Baseboard, Heat pump, Electric  Central     NaN    8115.0\n2         3406 Glorus Pl Silver Spring MD 20902    785000.0   5.0    5.0     5872.0  Single Family      2006.0                      Forced air  Central     NaN   10890.0\n3  11703 College View Dr Silver Spring MD 20902    475000.0   4.0    2.0     1982.0  Single Family      1951.0                 Forced air, Gas  Central     NaN    6930.0\n4         3400 Glorus Pl Silver Spring MD 20902    395000.0   4.0    3.0     1914.0  Single Family      1953.0                None, Forced air  Central     NaN    7178.0\n5    11714 Veirs Mill Rd Silver Spring MD 20902    383000.0   6.0    3.0     1836.0  Single Family      1953.0                      Forced air  Central     NaN    6812.0\n6      3402 Pendleton Dr Silver Spring MD 20902    340000.0   2.0    1.0      882.0  Single Family      1951.0                      Forced air  Central     NaN    7609.0\n\n--- 15.11016297340393 seconds ---\n```\n\n## Contact Info\n\n- @MattThomas9\n- @AmritPatel\n\n\n## License\n[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FMattThomas9%2FHome-Buyer-Fire.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2FMattThomas9%2FHome-Buyer-Fire?ref=badge_large)\n",
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
