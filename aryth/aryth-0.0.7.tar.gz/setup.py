# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aryth',
 'aryth.bound',
 'aryth.bound.entries',
 'aryth.bound.matrix',
 'aryth.bound.vector',
 'aryth.bound_entries',
 'aryth.bound_matrix',
 'aryth.bound_vector',
 'aryth.comparison',
 'aryth.enum',
 'aryth.enum.bound_keys',
 'aryth.math',
 'aryth.stat']

package_data = \
{'': ['*']}

install_requires = \
['intype>=0.0.2', 'texting>=0.0.2', 'veho>=0.0.4']

setup_kwargs = {
    'name': 'aryth',
    'version': '0.0.7',
    'description': 'numerical & statistics functions',
    'long_description': "## aryth\n##### numerical & statistics functions\n\n### Usage\n```python\nfrom aryth.bound_vector import max_by, min_by\n\ncities = [\n    'jakarta',\n    'bern',\n    'san fransisco',\n    '',\n    'paris',\n]\nprint(max_by(cities, len))\nprint(min_by(cities, len))\n```",
    'author': 'Hoyeung Wong',
    'author_email': 'hoyeungw@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hoyeungw/aryth.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
