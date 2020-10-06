# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pnmap']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0', 'scapy>=2.4.3,<3.0.0']

entry_points = \
{'console_scripts': ['pnmap = pnmap.console:main']}

setup_kwargs = {
    'name': 'pnmap',
    'version': '0.1.1',
    'description': 'A simplified Python implementation of nmap',
    'long_description': '# pnmap\nA simplified Python implementation of nmap (network mapper/port scanner).\n\n<img src="img/snake_eye.jpg" alt="pnmap">\n\n## Features\n\n- Quick and easy multi-target subnet scans.\n- Single target external scans.\n- UDP and TCP scans.\n- Often [faster](benchmarks.pdf) than nmap for simple scans, due to program simplicity.\n\n## Installation\n``` pip3 install pnmap ```\n\n## Usage\n- For quick subnet scans:\n```sudo pnmap```\n- For additional configuration, utilize help menu:\n``` pnmap --help ```\n\n- See [outputs](https://github.com/veyga/pnmap/tree/master/output) for specific use cases.\n\n## Additional Information\n- As pnmap utilizes packet injection, it must be run as sudo\n- Due to network briding, pnmap does not work deterministically inside VM\'s (e.g. Virtualbox, VMWare)\n- Results which return as "closed" implies the port returned a response\n- Results which return "filtered" are due to connection issues or are filtered by a firewall.\n\n## Screenshots\n<i>Subnet Scan</i></br></br>\n![Subet Scan](img/subnet_scan.png)\n</br>\n\n<i>Help</i></br></br>\n![Help Menu](img/help.png)\n</br>\n',
    'author': 'Andrew Stefanich',
    'author_email': 'andrewstefanich@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/veyga/pnmap',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
