# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['timespeaker']

package_data = \
{'': ['*'], 'timespeaker': ['resources/*']}

install_requires = \
['gtts>=2.1.1,<3.0.0', 'playsound>=1.2.2,<2.0.0']

setup_kwargs = {
    'name': 'timespeaker',
    'version': '0.1.0',
    'description': 'Announce the time every hour similar to Mac OS X. Say the Time using Google TTS or espeak.',
    'long_description': None,
    'author': 'Wallace Silva',
    'author_email': 'contact@wallacesilva.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
