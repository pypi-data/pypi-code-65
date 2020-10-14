# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['timespeaker']
install_requires = \
['gtts>=2.1.1,<3.0.0', 'pyttsx3>=2.90,<3.0']

entry_points = \
{'console_scripts': ['timespeaker = timespeaker.timespeaker:main']}

setup_kwargs = {
    'name': 'timespeaker',
    'version': '0.1.1',
    'description': 'Announce the time every hour similar to Mac OS X. Say the Time using Google TTS or espeak.',
    'long_description': None,
    'author': 'Wallace Silva',
    'author_email': 'contact@wallacesilva.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
