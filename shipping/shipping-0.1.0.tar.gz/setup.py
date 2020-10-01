# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['shipping', 'shipping.cli', 'shipping.configs']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'coloredlogs>=14.0,<15.0',
 'pydantic>=1.6.1,<2.0.0',
 'pyyaml>=5.3.1,<6.0.0']

entry_points = \
{'console_scripts': ['shipping = shipping.__main__:main']}

setup_kwargs = {
    'name': 'shipping',
    'version': '0.1.0',
    'description': 'Cli utility for deploying packages',
    'long_description': '# Shipping :ship: \n\nCli utility for deploying packages.\n\n## Idea\n\nTo simplify the process of deploying packages on different servers and in different ways. Currently there is support for deploying packages in conda environments, however it is being built with other methods such as containers, poetry etc in mind.\n\nThere are two configs in use, one is to describe the host environment and the other will hold specific instructions for a package.\n\nAll suggestions are welcome.\n\n## Example usage\n\n```\n$cat configs/server1/prod.yaml\n---\nhostname: computer1\nlog_file: /logs/production_deploy_log.txt\n\n\n$cat configs/server1/scout_production.yaml\n---\ntool: scout\nenv_name: P_scout\ndeploy_method: pip\n\n$shipping --host-info configs/server1.yaml deploy --config configs/scout.yaml\n```\n\nThis command will deploy the tool `scout` into the conda environment `P_scout` on the server `computer1` and log who deployed what version and when.\n\nThere will be different use cases where the deployment process involves restarting a server or installing dependencies with [yarn][yarn] etc that we will support.\n\n\n[yarn]: https://yarnpkg.com',
    'author': 'Måns Magnusson',
    'author_email': 'mans.magnusson@scilifelab.se',
    'maintainer': 'Måns Magnusson',
    'maintainer_email': 'mans.magnusson@scilifelab.se',
    'url': 'https://github.com/ClinicalGenomics/shipping/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
