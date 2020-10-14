# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['intype']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'intype',
    'version': '0.0.3',
    'description': 'dynamic type infer',
    'long_description': "## intype\n##### dynamic infer type\n\n### Usage\n```python\nfrom intype import has_literal\nword = 'chocolate'\nprint(has_literal(word))\n```",
    'author': 'Hoyeung Wong',
    'author_email': 'hoyeungw@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hoyeungw/intype',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
