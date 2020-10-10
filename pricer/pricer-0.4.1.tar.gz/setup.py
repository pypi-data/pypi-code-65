# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pricer']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML==5.2',
 'SLPP==1.2',
 'beautifulsoup4>=4.9.1,<5.0.0',
 'click==6.7',
 'deepdiff>=5.0.2,<6.0.0',
 'fastparquet==0.3.3',
 'importlib_metadata>=1.7.0,<2.0.0',
 'pandas==1.0.1',
 'pandera>=0.4.5,<0.5.0',
 'seaborn==0.9.0',
 'selenium>=3.141.0,<4.0.0',
 'sklearn>=0.0,<0.1',
 'tqdm>=4.49.0,<5.0.0']

entry_points = \
{'console_scripts': ['pricer = pricer.run:main']}

setup_kwargs = {
    'name': 'pricer',
    'version': '0.4.1',
    'description': 'Use WoW addon data to optimize auction buying and selling policies',
    'long_description': "# Pricer for WoW Auctions\n\n[![Tests](https://github.com/bluemania/wow_auctions/workflows/Tests/badge.svg)](https://github.com/bluemania/wow_auctions/actions?workflow=Tests)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Codecov](https://codecov.io/gh/bluemania/wow_auctions/branch/master/graph/badge.svg)](https://codecov.io/gh/bluemania/wow_auctions)\n[![PyPI](https://img.shields.io/pypi/v/pricer.svg)](https://pypi.org/project/pricer/)\n[![Documentation Status](https://readthedocs.org/projects/pricer/badge/?version=latest)](https://pricer.readthedocs.io/en/latest/?badge=latest)\n\n## About the project\n\nPricer for WoW Auction is a command line tool to helps users automate the decision making required to make profit on the World of Warcraft classic auction house.\nIt does so by reading addon data, using historical pricing information from [booty bay](bootybaygazette.com), and user specified preference, to calculate policies.\nThese policies take all available information to produce optimal actions for items, i.e. buying volume, selling low, selling high and crafting.\nThe policies overwrite the addon data, so that upon re-entering the game, the interface is ready to enact the optimal actions.\n\nThis is primarily a hobby project.\nMy aim is to learn about good software development practices, and apply my data science skills to an interesting problem.\nAnd the extra gold makes raiding even more fun!\n\nI did some [twitch streaming](https://www.twitch.tv/bluemania2) for a while, where I discussed the project goals and showed how things worked in more detail.\n\n## Built with\n\nMajor frameworks include:\n\n* Python 3+\n* Chromedriver and selenium - for booty bay data\n* Nox - for CI/CD process\n* Poetry - For dependencies, virtual environment, versioning and packaging\n\nRequirements for World of Warcraft classic include:\n\n* An active World of Warcraft account\n* An active Booty Bay Gazette subscription\n* ArkInventory addon - inventory tracking\n* Auctioneer addon - scanning auctions and enacting buy and sell policies\n* Beancounter addon - tracking player auction activity (comes with auctioneer)\n* Trade Skill Master - enacting crafting policies, also recommended to speed up moving items to bank and buying materials from vendors\n\n## Getting started\n\nThe following are instructions on how to set up the project locally.\n\nThe latest stable code can be found on [pypi](https://pypi.org/project/pricer/).\n\nDownload locally using:\n\n```bash\npip install pricer\n```\n\nFor development, clone the repository.\n\nThis project uses [poetry](https://python-poetry.org/) to manage dependencies, virtual environments, versioning and packaging.\n\n```bash\npoetry install\n```\n\n# Usage\n\n## User configuration\n\nIt is recommended to edit the `config/user_items.yaml` file, as this is the primary mechanism that users can select items of interest for buying, selling and crafting.\nRefer to the file to interpret the structure, ensure that items are named correctly.\n\nThe `config/user_settings.yaml` file should also be edited with information about paths to installations (WoW and Chromedriver), and active accounts.\nAccount names can be referenced from your WoW directory.\nBooty Bay information should be specified to be specific to your server.\nSpecify at least one of your characters as an `ahm` (auction house main), with others as `mule`.\n\nYou can optionally create a `SECRETS.yaml` file in the root directory with the following format.\nThis is useful to help automate the booty bay data feed, but not required.\nWe highly recommend using the Blizzard authenticator (stay safe!).\n\n```yaml\naccount: youraccount\npassword: yourpassword\n```\n\n## Running the program\n\nIt is recommended to perform a auction scan immediately prior to running the program.\nYou will need to be logged out while the program is running, as this is the only way the latest addon data can be loaded, and modified.\n\nRun the program using the following command from command line:\n\n```bash\npricer\n```\n\nAdditional flags can, and should be entered:\n\n* `-v` or `-vv` is useful for debugging purposes\n* `-b` is used to seek a refresh of Booty Bay data; it is recommended to seek an update at least once every day or so.\n* `-h` for help on additional flags and functionality that may be available\n\nIf the run has been successful, you should see some tabular information printed in the console.\nThis will include information about what items to make and expected profits for feasible selling items.\n\nYou should see Auctioneer data has been changed, so that (feasible) sell prices and thresholds for buying using snatch have been set.\n\n## Tests and tooling\n\nThis project seeks to use modern code quality and CI/CD tooling including\n\n* Dependency management, virtual env and packaging (poetry)\n* Linting (black, flake8, darglint)\n* Type checking (mypy)\n* Testing (pytest, pandera, codecov)\n* Docs (sphinx, autodoc)\n* Task automation CI/CD (nox, pre-commit, github actions, pr-labeler, release-drafter)\n* Publishing (pypi, readthedocs)\n\n# Contributing\n\nThis project is pre-release and under development. \n\nUsers are welcome to try the program, fork, or [contribute](CONTRIBUTING.md), however [support](SUPPORT.md) is not guarenteed.\n\nFollow this link for instructions on managing [releases](RELEASE.md).\n\n# License\n\nAll assets and code are under the MIT LICENSE and in the public domain unless specified otherwise.\nSee the [license](LICENSE) for more info.\n\n# Contact\n\nFeel free to reach out in-game; you'll see me on Grobbulus on Amazona. \n\nYou can leave an open issue seeking to connect and I'll get back to you.\n\nI also occassionally stream project development on [twitch](https://www.twitch.tv/bluemania2).\n",
    'author': 'bluemania',
    'author_email': 'damnthatswack@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bluemania/wow_auctions',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
