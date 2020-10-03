# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['torch_optim_sparse']

package_data = \
{'': ['*']}

install_requires = \
['torch>=1.6.0,<2.0.0']

setup_kwargs = {
    'name': 'torch-optim-sparse',
    'version': '0.1.3',
    'description': 'PyTorch optimizers with sparse momentum and weight decay',
    'long_description': None,
    'author': 'Karl Higley',
    'author_email': 'kmhigley@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
