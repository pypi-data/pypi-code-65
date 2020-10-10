# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pnp',
 'pnp.config',
 'pnp.console',
 'pnp.engines',
 'pnp.plugins',
 'pnp.plugins.pull',
 'pnp.plugins.push',
 'pnp.plugins.udf',
 'pnp.shared']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=2.11.2,<3.0.0',
 'aiohttp>=3.6.2,<4.0.0',
 'async_generator>=1.10,<2.0',
 'asyncio>=3.4.3,<4.0.0',
 'asyncws>=0.1,<0.2',
 'attrs>=19.3.0,<20.0.0',
 'binaryornot>=0.4.4,<0.5.0',
 'cachetools>=4.1.0,<5.0.0',
 'cronex>=0.1.3,<0.2.0',
 'dictmentor>=0.2.2,<0.3.0',
 'docopt>=0.6.2,<0.7.0',
 'glom>=19.10.0,<20.0.0',
 'influxdb>=5.3.0,<6.0.0',
 'paho-mqtt>=1.5.0,<2.0.0',
 'pathspec>=0.8.0,<0.9.0',
 'psutil>=5.7.0,<6.0.0',
 'python-box<=3.4.6',
 'pytz>=2020.1,<2021.0',
 'requests>=2.23.0,<3.0.0',
 'ruamel.yaml>=0.16.10,<0.17.0',
 'sanic>=18.12.0,<19.0.0',
 'sanic_openapi==0.6.0',
 'sanic_prometheus>=0.2.0,<0.3.0',
 'schedule>=0.6.0,<0.7.0',
 'schema>=0.7.2,<0.8.0',
 'schiene>=0.23,<0.24',
 'slacker>=0.14.0,<0.15.0',
 'syncasync>=20180812,<20180813',
 'typeguard>=2.7.1,<3.0.0',
 'typing-extensions>=3.7.4,<4.0.0',
 'tzlocal>=2.0.0,<3.0.0']

extras_require = \
{'dht': ['Adafruit_DHT>=1.3.2,<2.0.0'],
 'dropbox': ['dropbox>=9.0.0,<10.0.0', 'urllib3>=1.20,<2.0'],
 'faceR': ['face-recognition>=1.2.2,<2.0.0', 'image>=1.5.24,<2.0.0'],
 'fitbit': ['fitbit>=0.3.0,<0.4.0'],
 'fritz:python_version >= "3.6" and python_version < "4.0"': ['fritzconnection>=1.2.0,<2.0.0'],
 'fswatcher': ['watchdog>=0.8.3,<0.9.0'],
 'ftp': ['pyftpdlib>=1.5.0,<2.0.0'],
 'gmail': ['google-api-python-client>=1.7.7,<2.0.0',
           'google-auth-httplib2>=0.0.3,<0.0.4',
           'google-auth-oauthlib>=0.2.0,<0.3.0'],
 'gpio': ['RPi.GPIO>=0.6.5,<0.7.0'],
 'miflora': ['miflora>=0.4.0,<0.5.0'],
 'pushbullet': ['pushbullet.py>=0.10.0,<0.11.0', 'urllib3>=1.20,<2.0'],
 'sound': ['numpy>=1.16.0,<2.0.0',
           'PyAudio>=0.2.11,<0.3.0',
           'scipy>=1.2.0,<2.0.0'],
 'speedtest': ['speedtest-cli>=2.1.0,<3.0.0']}

entry_points = \
{'console_scripts': ['pnp = pnp.console.pnp:main',
                     'pnp_gmail_tokens = pnp.console.pnp_gmail_tokens:main',
                     'pnp_record_sound = pnp.console.pnp_record_sound:main']}

setup_kwargs = {
    'name': 'pnp',
    'version': '0.25.0',
    'description': "Pull 'n' Push",
    'long_description': '# Pull \'n\' Push\n\n[![Python](https://img.shields.io/badge/Python-3.5%20%7C%203.6%20%7C%203.7-green.svg)](https://www.python.org/)\n[![PyPI version](https://badge.fury.io/py/pnp.svg)](https://badge.fury.io/py/pnp)\n[![Docs](https://readthedocs.org/projects/pnp/badge/?version=stable)](https://pnp.readthedocs.io/en/stable/?badge=stable)\n[![GitHub Activity](https://img.shields.io/github/commit-activity/y/HazardDede/pnp.svg)](https://github.com/HazardDede/pnp/commits/master)\n[![Build Status](https://travis-ci.org/HazardDede/pnp.svg?branch=master)](https://travis-ci.org/HazardDede/pnp)\n[![Coverage Status](https://coveralls.io/repos/github/HazardDede/pnp/badge.svg?branch=master)](https://coveralls.io/github/HazardDede/pnp?branch=master)\n[![Docker: hub](https://img.shields.io/badge/docker-hub-brightgreen.svg)](https://cloud.docker.com/u/hazard/repository/docker/hazard/pnp)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n![Project Maintenance](https://img.shields.io/badge/maintainer-Dennis%20Muth%20%40HazardDede-blue.svg)\n\n> Pulls data from sources and pushes it to sinks with optional transformations in between.\n\n## Installation\n\n    pip install pnp\n\nInstallation with extras:\n    \n    pip install pnp[fswatcher,faceR]\n\nPlease consult the [component documentation](https://pnp.readthedocs.io/en/stable/plugins/index.html) to see if a\ncomponent requires an extra or not.\n\n## Getting started\n\nDefine `pulls` to fetch / pull data from source systems.\nDefine one `push` or multiple `pushes` per pull to transfer the pulled data anywhere else (you only need a plugin that \nknows how to handle the target). You configure your pipeline in `yaml`:\n\n```yaml\ntasks:\n  - name: hello-world\n    pull:\n      plugin: pnp.plugins.pull.simple.Repeat\n      args:\n        interval: 1s\n        repeat: "Hello World"\n    push:\n      - plugin: pnp.plugins.push.simple.Echo\n```\n        \nCopy this configuration and create the file `helloworld.yaml`. Run it:\n\n    pnp helloworld.yaml\n\nThis example yields the string `Hello World` every second.\n\n**Hint**: You can validate your config without actually executing it with\n\n```bash\n   pnp --check helloworld.yaml\n```\n\nIf you want to learn more please see the documentation at [Read the Docs](https://pnp.readthedocs.io/en/stable/).\n',
    'author': 'Dennis Muth',
    'author_email': 'd.muth@gmx.net',
    'maintainer': 'Dennis Muth',
    'maintainer_email': 'd.muth@gmx.net',
    'url': 'https://pnp.readthedocs.io/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
