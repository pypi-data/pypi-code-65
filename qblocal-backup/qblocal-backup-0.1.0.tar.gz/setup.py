# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qblocal_backup']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'qblocal-backup',
    'version': '0.1.0',
    'description': 'a local backup tool for qbittorrent without call webui api.',
    'long_description': '# qblocal_backup\n\na local backup tool for qbittorrent without call webui api.\n\n## Usage\n\n``` cmd\npython -m qblocal_backup <QBITTORRENT_CONF> <DEST_LOCATION>\n```\n\n`<DEST_LOCATION>` should be a directory.\n',
    'author': 'Cologler',
    'author_email': 'skyoflw@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Cologler/qblocal_backup-python',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
