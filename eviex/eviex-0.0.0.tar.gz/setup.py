# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eviex']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'eviex',
    'version': '0.0.0',
    'description': 'EVents Inverted indEX',
    'long_description': None,
    'author': 'Lou Marvin Caraig',
    'author_email': 'loumarvincaraig@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
