# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['textomatic', 'textomatic.app', 'textomatic.processor']

package_data = \
{'': ['*']}

install_requires = \
['clevercsv>=0.6.4,<0.7.0',
 'click>=7.1.2,<8.0.0',
 'prompt-toolkit>=3.0.7,<4.0.0',
 'pygments>=2.7.1,<3.0.0',
 'pyparsing>=2.4.7,<3.0.0',
 'pyperclip>=1.8.0,<2.0.0',
 'tabulate>=0.8.7,<0.9.0']

entry_points = \
{'console_scripts': ['tm = textomatic.main:main']}

setup_kwargs = {
    'name': 'textomatic',
    'version': '0.1.0',
    'description': 'Scratchpad for tabular data transformations',
    'long_description': None,
    'author': 'Dan Kilman',
    'author_email': 'dankilman@gmail.com',
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
