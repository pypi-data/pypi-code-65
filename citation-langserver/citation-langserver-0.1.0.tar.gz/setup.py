# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['citation_langserver']

package_data = \
{'': ['*']}

install_requires = \
['bibparse>=1.0.0,<2.0.0', 'pygls>=0.9.0,<0.10.0']

entry_points = \
{'console_scripts': ['citation-langserver = citation_langserver.cli:cli']}

setup_kwargs = {
    'name': 'citation-langserver',
    'version': '0.1.0',
    'description': 'A language server for managing citations stored in BibTeX and BibLaTeX files.',
    'long_description': None,
    'author': 'oncomouse',
    'author_email': 'oncomouse@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/oncomouse/citation-langserver',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
