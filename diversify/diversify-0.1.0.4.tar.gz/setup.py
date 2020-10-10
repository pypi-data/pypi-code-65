# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['diversify']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.6.2,<4.0.0',
 'click>=7.1.2,<8.0.0',
 'colorama>=0.4.3,<0.5.0',
 'numpy>=1.19.2,<2.0.0',
 'pandas>=1.1.2,<2.0.0',
 'spotipy>=2.16.0,<3.0.0']

entry_points = \
{'console_scripts': ['diversify = diversify.main:diversify']}

setup_kwargs = {
    'name': 'diversify',
    'version': '0.1.0.4',
    'description': 'A small playlist generator for spotify',
    'long_description': "# Diversify\n\n## The Project\n\nDiversify is a playlist generator based on the [Spofity WEB API](https://developer.spotify.com/web-api/) and the [Spotipy module](http://spotipy.readthedocs.io/en/latest/)\nthat aims to use concepts of AI to suggest playlists based on musical preferences between multiple people.\n\n## Goals\n\nThe goal is to use AI algorithms to generate a spotify playlist based on a user's preference and\na friend of his choice. Currently the script will use a genetic algorthm to generate the playlists\nbut this may improve in the future.\n\n## How to install\n\n- First you need to get your spotify API key and save it to the .env file. \n\t- Go to [spotify application web page](https://developer.spotify.com/dashboard/),\n\t- login with your spotify account and create a new app\n\t- put whatever name you'd like on the project info and say no to commercial integration\n\t- click on edit settings and whitelist https://edujtm.github.io/diversify/redirect\n\t- get your client ID and client secret (by clicking *show client secret*)\n\t- put them on a [config.ini](config.ini.example) file and move it to  `$HOME/.config/diversify/`\n\t- run `pip install diversify` \n\t- run `diversify --help` to see if everything went ok.\n\n## How to run\n\n```\n$ diversify login\n$ diversify playlist PLAYLIST NAME\n```\n\n## How to contribute\n\n- This project uses [poetry](https://python-poetry.org/) for dependency management\n- Clone this repo: `git clone https://github.com/edujtm/diversify.git`\n- `cd diversify` and `poetry install`\n- Then run `poetry shell`\n\n",
    'author': 'Eduardo Macedo',
    'author_email': 'eduzemacedo@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
