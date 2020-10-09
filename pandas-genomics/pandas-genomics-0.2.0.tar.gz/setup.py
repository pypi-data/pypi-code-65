# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pandas_genomics', 'pandas_genomics.arrays', 'pandas_genomics.io']

package_data = \
{'': ['*']}

install_requires = \
['ipython[docs]>=7.18.1,<8.0.0',
 'numpydoc[docs]>=1.1.0,<2.0.0',
 'pandas>=1.1,<2.0',
 'sphinx-copybutton[docs]>=0.3.0,<0.4.0',
 'sphinx_rtd_theme[docs]>=0.5.0,<0.6.0']

extras_require = \
{'docs': ['sphinx>=3.2.1,<4.0.0']}

setup_kwargs = {
    'name': 'pandas-genomics',
    'version': '0.2.0',
    'description': 'Pandas ExtensionDtypes and ExtensionArray for working with genomics data',
    'long_description': '<div align="center">\n<img src="docs/_static/logo.png" alt="pandas_genomics logo"/>\n</div>\n\n<br/>\n\n<div align="center">\n\n<!-- Python version -->\n<a href="https://pypi.python.org/pypi/pandas-genomics">\n<img src="https://img.shields.io/badge/python-3.7+-blue.svg?style=for-the-badge" alt="PyPI version"/>\n</a>\n<!-- PyPi -->\n<a href="https://pypi.org/project/pandas-genomics/">\n<img src="https://img.shields.io/pypi/v/pandas-genomics.svg?style=for-the-badge" alt="pypi" />\n</a>\n<!-- Build status -->\n<a href="https://travis-ci.org/HallLab/pandas-genomics?branch=master">\n<img src="https://img.shields.io/travis/HallLab/pandas-genomics.svg?style=for-the-badge" alt="Build Status" />\n</a>\n<!-- Test coverage -->\n<a href="https://coveralls.io/github/HallLab/pandas-genomics?branch=master">\n<img src="https://img.shields.io/codecov/c/gh/HallLab/pandas-genomics.svg?style=for-the-badge" alt="Coverage Status"/>\n</a>\n<!-- License -->\n<a href="https://opensource.org/licenses/BSD-3-Clause">\n<img src="https://img.shields.io/pypi/l/pandas-genomics?style=for-the-badge" alt="license"/>\n</a>\n</div>\n\n<br/>\n\nPandas ExtensionDtypes and ExtensionArray for working with genomics data\n',
    'author': 'John McGuigan',
    'author_email': 'jrm5100@psu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/HallLab/pandas-genomics/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
