# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gsan']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0',
 'colorama>=0.4.1,<0.5.0',
 'ndg-httpsclient>=0.5.1,<0.6.0',
 'pandas>=0.25.3,<0.26.0',
 'pyasn1>=0.4.8,<0.5.0',
 'pyopenssl>=19.1,<20.0',
 'tldextract>=2.2,<3.0']

entry_points = \
{'console_scripts': ['gsan = gsan.cli:cli']}

setup_kwargs = {
    'name': 'gsan',
    'version': '4.2.3',
    'description': 'Extract subdomains from HTTPS sites',
    'long_description': None,
    'author': 'Franccesco Orozco',
    'author_email': 'franccesco@codingdose.info',
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
