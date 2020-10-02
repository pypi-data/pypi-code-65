# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jedi_xlsx']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.1.2,<2.0.0',
 'toolz>=0.11.1,<0.12.0',
 'xlrd[dev]>=1.2.0,<2.0.0',
 'xlsxwriter>=1.3.6,<2.0.0']

setup_kwargs = {
    'name': 'jedi-xlsx',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'JediHero',
    'author_email': 'hansen.rusty@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
