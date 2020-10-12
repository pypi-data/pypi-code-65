# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['shipping', 'shipping.cli', 'shipping.configs', 'shipping.deploy']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'coloredlogs>=14.0,<15.0',
 'pydantic>=1.6.1,<2.0.0',
 'pytz>=2020.1,<2021.0',
 'pyyaml>=5.3.1,<6.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1.0,<2.0']}

entry_points = \
{'console_scripts': ['shipping = shipping.__main__:main']}

setup_kwargs = {
    'name': 'shipping',
    'version': '0.2.2',
    'description': 'Cli utility for deploying packages',
    'long_description': '# Shipping :ship: \n\n![Shipping tests][github-url] [![Coverage Status][coveralls-image]][coveralls-url] [![CodeFactor][codefactor-image]][codefactor-url] [![Code style: black][black-image]][black-url]\n\n\nCli utility for deploying packages.\n\n## Idea\n\nTo simplify the process of deploying packages on different servers and in different ways. Currently there is support for deploying packages in conda environments, however it is being built with other methods such as containers, poetry etc in mind.\n\nThere are two configs in use, one is to describe the host environment and the other will hold specific instructions for a package.\n\nAll suggestions are welcome.\n\n## Example usage\n\n```\n$cat configs/server1/prod.yaml\n---\nhostname: computer1\nlog_file: /logs/production_deploy_log.txt\n\n\n$cat configs/server1/scout_production.yaml\n---\ntool: scout\nenv_name: P_scout\ndeploy_method: pip\n\n$shipping --host-info configs/server1/prod.yaml deploy --config configs/server1/scout_production.yaml\n```\n\nThis command will deploy the tool `scout` into the conda environment `P_scout` on the server `computer1` and log who deployed what version and when.\n\nThere will be different use cases where the deployment process involves restarting a server or installing dependencies with [yarn][yarn] etc that we will support.\n\n\n[yarn]: https://yarnpkg.com\n[pypi]: https://pypi.python.org/pypi/shipping/\n[coveralls-url]: https://coveralls.io/r/Clinical-Genomics/shipping\n[coveralls-image]: https://img.shields.io/coveralls/Clinical-Genomics/shipping.svg?style=flat-square\n[github-url]: https://github.com/Clinical-Genomics/shipping/workflows/Tests/badge.svg\n[codefactor-image]: https://www.codefactor.io/repository/github/clinical-genomics/shipping/badge\n[codefactor-url]: https://www.codefactor.io/repository/github/clinical-genomics/shipping\n[black-image]: https://img.shields.io/badge/code%20style-black-000000.svg\n[black-url]: https://github.com/psf/black',
    'author': 'Måns Magnusson',
    'author_email': 'mans.magnusson@scilifelab.se',
    'maintainer': 'Måns Magnusson',
    'maintainer_email': 'mans.magnusson@scilifelab.se',
    'url': 'https://github.com/ClinicalGenomics/shipping/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
