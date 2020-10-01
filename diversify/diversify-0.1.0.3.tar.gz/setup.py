# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['diversify', 'diversify.tf']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.6.2,<4.0.0',
 'click>=7.1.2,<8.0.0',
 'colorama>=0.4.3,<0.5.0',
 'numpy>=1.19.2,<2.0.0',
 'pandas>=1.1.2,<2.0.0',
 'python-dotenv>=0.14.0,<0.15.0',
 'spotipy>=2.16.0,<3.0.0']

entry_points = \
{'console_scripts': ['diversify = diversify.main:diversify']}

setup_kwargs = {
    'name': 'diversify',
    'version': '0.1.0.3',
    'description': 'A small playlist generator for spotify',
    'long_description': '# Diversify\n\n**Warning:** This project is still in a very alpha stage. I\'m currently working on a backend for it so the user authentication becomes more friendly.\n\n## The Project\n\nDiversify is a playlist generator based on the [Spofity WEB API](https://developer.spotify.com/web-api/) and the [Spotipy module](http://spotipy.readthedocs.io/en/latest/)\nthat aims to use concepts of AI to suggest playlists based on musical preferences between multiple people.\n\nThis project was heavily inspired by this [article](https://dev.to/ericbonfadini/finding-my-new-favorite-song-on-spotify-4lgc) by \n[@ericbonfadini](https://twitter.com/ericbonfadini) and it\'s basically just an extra functionality in his analysis.\n\n## Goals\n\nThe goal is to use AI algorithms to generate a spotify playlist based on a user\'s preference and\na friend of his choice. Currently the script will use a genetic algorthm to generate the playlists\nbut this may improve in the future.\n\n## How to run\n\n- First you need to get your spotify API key and save it to the .env file. \n\t- Go to [spotify application web page](https://developer.spotify.com/dashboard/),\n\t- login with your spotify account and create a new app\n\t- put whatever name you\'d like on the project info and say no to commercial integration\n\t- get your client ID and client secret (by clicking *show client secret*)\n\t- put them on your .env.example file and rename it to .env \n\t- click on edit settings and whitelist https://edujtm.github.io/diversify/redirect\n\nThese steps are annoying but are needed because I didn\'t deploy this app somewhere yet, I have plans to deploy it once I make it faster.\n\n- Clone this repo: `git clone https://github.com/edujtm/diversify.git`\n\n- Create a new environment with your package manager or install the dependencies in environment.yml with pip. <br/>\n\tPersonally I use anaconda, so it\'s just a matter of running `conda env create --file=environmnent.yml` and then `conda activate diversify`\n\n- With the previous step done, you can import the interfacespfy module in an interactive prompt\n\n```Python\nfrom diversify.session import SpotifySession\nspfy = SpotifySession()\n\nplaylists = spfy.get_user_playlists("other_username")\nsaved_songs = spfy.get_favorite_songs()\n```\n\n- You can login from the terminal by running `diversify login`\n\n- You can generate playlists by running `diversify playlist`. (run diversify playlist --help for more info) <br/>\n    Example: `diversify playlist --friend my_friend_id my awesome playlist`\n\n',
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
