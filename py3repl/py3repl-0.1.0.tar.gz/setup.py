# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py3repl']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.3,<0.5.0']

entry_points = \
{'console_scripts': ['pyrepl = py3repl.pyrepl:repl']}

setup_kwargs = {
    'name': 'py3repl',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'amalshaji',
    'author_email': 'amalshajid@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
