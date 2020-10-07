# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simpleatm']

package_data = \
{'': ['*']}

install_requires = \
['xarray>=0.15,<0.16']

setup_kwargs = {
    'name': 'simpleatm',
    'version': '0.1.0',
    'description': 'Lightweight Python package for calculating the atmospheric transmission',
    'long_description': "# simpleatm\n\n[![PyPI](https://img.shields.io/pypi/v/simpleatm.svg?label=PyPI&style=flat-square)](https://pypi.org/pypi/simpleatm/)\n[![Python](https://img.shields.io/pypi/pyversions/simpleatm.svg?label=Python&color=yellow&style=flat-square)](https://pypi.org/pypi/simpleatm/)\n[![Test](https://img.shields.io/github/workflow/status/deshima-dev/simpleatm/Test?logo=github&label=Test&style=flat-square)](https://github.com/deshima-dev/simpleatm/actions)\n[![License](https://img.shields.io/badge/license-MIT-blue.svg?label=License&style=flat-square)](LICENSE)\n\nLightweight Python package for calculating the atmospheric transmission\n\n## Overview\n\n[simpleatm] is a Python package which calculates (sub)millimeter atmospheric transmission as a function of precipitable water vapor (PWV) and frequency.\nThe package includes pre-calculated transmission datasets at various observation sites by the [ATM model] (Pardo et al. 2001).\nMoreover, since a dataset is loaded as the [xarray]'s DataArray format, interpolation, plotting, and saving features are provided by default.\nTherefore, [simpleatm] would be useful in fast and approximate sensitivity calculation of a telescope instrument.\n\n## Requirements\n\n- **Python:** 3.6, 3.7, or 3.8 (tested by the authors)\n- **Dependencies:** See [pyproject.toml](https://github.com/deshima-dev/simpleatm/blob/master/pyproject.toml)\n\n## Installation\n\n```shell\n$ pip install simpleatm\n```\n\n## Usage\n\nTo be updated after the release of [v0.2.0](https://github.com/deshima-dev/simpleatm/milestone/2).\n\n## For developers\n\n```shell\n$ git clone https://github.com/deshima-dev/simpleatm.git\n$ cd simpleatm\n$ scripts/setup\n```\n\n## References\n\n- [ATM model]: pre-calculated table was obtained here\n- [xarray]: N-D labeled arrays and datasets in Python\n\n[simpleatm]: https://pypi.org/project/simpleatm/\n[ALMA]: https://almascience.nao.ac.jp/\n[ATM model]: https://almascience.nao.ac.jp/about-alma/atmosphere-model/\n[Poetry]: https://python-poetry.org/\n[xarray]: https://xarray.pydata.org/en/stable/\n",
    'author': 'Akio Taniguchi',
    'author_email': 'taniguchi@a.phys.nagoya-u.ac.jp',
    'maintainer': 'Yohei Togami',
    'maintainer_email': 'y.togami@a.phys.nagoya-u.ac.jp',
    'url': 'https://github.com/deshima-dev/simpleatm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
