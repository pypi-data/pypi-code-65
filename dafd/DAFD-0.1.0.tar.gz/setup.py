# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dafd',
 'dafd.bin',
 'dafd.core_logic',
 'dafd.helper_scripts',
 'dafd.model_data',
 'dafd.models.forward_models',
 'dafd.models.regime_models']

package_data = \
{'': ['*'],
 'dafd.helper_scripts': ['experimental_data/*'],
 'dafd.models.forward_models': ['saved/*'],
 'dafd.models.regime_models': ['saved/*']}

install_requires = \
['keras>=2.4.3,<3.0.0',
 'matplotlib>=3.3.1,<4.0.0',
 'pandas>=1.1.2,<2.0.0',
 'scikit-learn>=0.23.2,<0.24.0',
 'tensorflow>=2.3.0,<3.0.0',
 'tqdm>=4.48.2,<5.0.0']

setup_kwargs = {
    'name': 'dafd',
    'version': '0.1.0',
    'description': 'Python package for the library for DAFD.',
    'long_description': None,
    'author': 'Radhakrishna Sanka',
    'author_email': 'rkrishnasanka@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
