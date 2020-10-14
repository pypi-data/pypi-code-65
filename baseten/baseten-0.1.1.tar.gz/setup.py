# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['baseten', 'baseten.common', 'baseten.examples', 'baseten.workflow']

package_data = \
{'': ['*'], 'baseten': ['templates/*']}

install_requires = \
['boto3>=1.9,<2.0',
 'click>=7.0,<8.0',
 'cloudpickle==1.6.0',
 'colorama>=0.4.3,<0.5.0',
 'coolname>=1.1.0,<2.0.0',
 'h5py>=2.10.0,<3.0.0',
 'jinja2>=2.10.3,<3.0.0',
 'joblib>=0.13.2,<0.14.0',
 'keyring>=19.2,<20.0',
 'libcst>=0.3.4,<0.4.0',
 'pandas>=0.25.1,<0.26.0',
 'requests>=2.22,<3.0',
 'tensorflow>=2.3.0,<3.0.0']

entry_points = \
{'console_scripts': ['baseten = baseten.cli:cli_group']}

setup_kwargs = {
    'name': 'baseten',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Amir Haghighat',
    'author_email': 'amir@baseten.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
