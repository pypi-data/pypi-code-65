# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aimgui', 'aimgui.renderers']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'aimgui',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Kurtis Fields',
    'author_email': 'kurtisfields@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
