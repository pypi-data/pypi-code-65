# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['hypermodern_python_cdavis']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'desert>=2020.1.6,<2021.0.0',
 'marshmallow>=3.8.0,<4.0.0',
 'requests>=2.24.0,<3.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=2.0.0,<3.0.0']}

entry_points = \
{'console_scripts': ['hypermodern-python-cdavis = '
                     'hypermodern_python_cdavis.console:main']}

setup_kwargs = {
    'name': 'hypermodern-python-cdavis',
    'version': '1.0.2',
    'description': 'The hypermodern Python project',
    'long_description': '[![Tests](https://github.com/cvdavis3/hypermodern-python-cdavis/workflows/Tests/badge.svg)](https://github.com/cvdavis3/hypermodern-python-cdavis/actions?workflow=Tests)\n[![Codecov](https://codecov.io/gh/cvdavis3/hypermodern-python-cdavis/branch/master/graph/badge.svg)](https://codecov.io/gh/cvdavis3/hypermodern-python-cdavis)\n[![PyPI](https://img.shields.io/pypi/v/hypermodern-python-cdavis.svg)](https://pypi.org/project/hypermodern-python-cdavis/)\n[![Read the Docs](https://readthedocs.org/projects/hypermodern-python-cdavis/badge/)](https://hypermodern-python-cdavis.readthedocs.io/)\n\n# hypermodern-python-cdavis\n\nCompanion repository for the Hypermodern Python article series<br>\nhttps://medium.com/@cjolowicz/hypermodern-python-d44485d9d769\n',
    'author': 'Colin Davis',
    'author_email': 'cvdavis3@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cvdavis3/hypermodern-python-cdavis',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
