# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nomnomdata', 'nomnomdata.nominode']

package_data = \
{'': ['*'], 'nomnomdata.nominode': ['samples/*']}

install_requires = \
['dunamai>=1.1.0,<2.0.0',
 'mergedeep>=1.3.0,<2.0.0',
 'nomnomdata-auth>=2.3.3,<3.0.0',
 'nomnomdata-cli>=0.1.8,<0.2.0',
 'omegaconf>=2.0.2,<3.0.0',
 'requests>=2.24.0,<3.0.0',
 'typing>=3.7.4,<4.0.0']

entry_points = \
{'nomnomdata.cli_plugins': ['nominode = nomnomdata.nominode.cli:cli']}

setup_kwargs = {
    'name': 'nomnomdata-nominode',
    'version': '0.3.0.post2.dev0',
    'description': 'Package containing tooling for interacting with nominodes',
    'long_description': '# nomnomdata-nominode\n\nCLI Project for interacting with nominode api\n\nsetup for your environment\n\npip install poetry\npoetry install\npip install pre-commit\npre-commit install\n',
    'author': 'Nom Nom Data Inc',
    'author_email': 'info@nomnomdata.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/nomnomdata/tools/nomnomdata-nominode',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
