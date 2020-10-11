# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pycites']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'click>=7.1.2,<8.0.0',
 'pandas>=1.0.5,<2.0.0',
 'requests>=2.24.0,<3.0.0',
 'tqdm>=4.46.1,<5.0.0']

entry_points = \
{'console_scripts': ['get_cites_data = pycites.cli:cli']}

setup_kwargs = {
    'name': 'pycites',
    'version': '0.1.3',
    'description': 'Package to download and interact with the CITES Trade Database in Python',
    'long_description': '# pycites\n`pycites` is a package to download and interact with the [CITES Trade Database](https://trade.cites.org/) using Python. [citesdb](https://github.com/ropensci/citesdb) exists for R users to load and analzyes this data, so we wanted a way to do the same!\n\nCurrently very much a work in progress.  Currently only downloads and loads data.\n\n## Installation\n`pip install pycites`\n\n## Usage instructions\nTo download the CITES Trade Database and load into a dataframe, run the following in a Jupyter notebook or Python shell:\n```python\nimport pycites\n\npycites.get_data()\ndf = pycites.load_data()\n```\nThis will download and extract the zip file from the CITES website, do some basic data validation (e.g. drop rows with missing or incorrect Years), and combine the data into a single compressed CSV file.  This uses a decent amount of memory, so may cause issues on a machines with low resource.\n\n## Roadmap\n- [ ] Release a CSV to make it easier for users to download and load data\n- [ ] Experiement with other data formats for better memory usage of data (currently pretty high)\n- [ ] Add a CLI for downloading data\n- [ ] Include metadata and other useful information, like `citesdb`\n- [ ] Add additional functionality for analysis (time series and network analyses), and integrate with other data sources (such as World Bank)\n- [ ] Setup CI and testing\n',
    'author': 'Lee Tirrell',
    'author_email': 'tirrell.le@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ltirrell/pycites',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
