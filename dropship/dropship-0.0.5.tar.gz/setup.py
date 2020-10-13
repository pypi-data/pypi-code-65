# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dropship']

package_data = \
{'': ['*'], 'dropship': ['ui/*']}

install_requires = \
['magic-wormhole>=0.12.0,<0.13.0',
 'pycairo<1.20',
 'pygobject<3.32',
 'trio-gtk>=3.0.0,<4.0.0',
 'trio>=0.17.0,<0.18.0']

entry_points = \
{'console_scripts': ['dropship = dropship:main']}

setup_kwargs = {
    'name': 'dropship',
    'version': '0.0.5',
    'description': 'Magic wormhole with a nice graphical interface',
    'long_description': '# Dropship\n\n[![Build Status](https://travis-ci.org/decentral1se/dropship.svg?branch=main)](https://travis-ci.org/decentral1se/dropship)\n\nLets try magic wormhole with a nice graphical interface.\n\n![Screen cast of dropship interface](https://vvvvvvaria.org/~r/dropship0.1.gif)\n\n_(click for video)_\n\n## Install\n\n> Coming Soon™\n\n## Develop\n\n### Documentation\n\nSee our [wiki](https://git.vvvvvvaria.org/rra/dropship/wiki).\n\n### Install for Hacking\n\nInstall [poetry](https://python-poetry.org/docs/#installation) and then install the package locally.\n\n```\n$ poetry install\n```\n\n### Run in Hackity Hack Hack Mode\n\n```bash\n$ poetry run dropship\n```\n\n### Updating dependencies\n\n- Change the bounds/versions/etc. in the [pyproject.toml](./pyproject.toml)\n- Run `poetry update`\n- Commit and push your changes\n\nThe [poetry.lock](./poetry.lock) file helps us all get the same dependencies.\n\n### Adding a Github Mirror\n\nWe use a Github mirror so we can have a [gratis automated release build](./.travis.yml).\n\nAdd the following to the bottom of your `.git/config`.\n\n```\n[remote "all"]\n  url = ssh://gitea@vvvvvvaria.org:12345/rra/dropship.git\n  url = git@github.com:decentral1se/dropship.git\n```\n\nThe `git push -u all main` will setup `git push` to automatically push to both remotes.\n\n### Make a new Release\n\n> Publishing binaries is disabled until we make further progress on [#3](https://git.vvvvvvaria.org/rra/dropship/issues/3)\n\n```bash\n$ git tag $mytag  # follow semver.org please\n$ git push\n```\n\nThe [Travis CI configuration](./.travis.yml) will run [a build](https://travis-ci.org/github/decentral1se/dropship) and [publish binaries here](https://github.com/decentral1se/dropship/releases).\n',
    'author': 'decentral1se',
    'author_email': 'hi@decentral1.se',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://git.vvvvvvaria.org/rra/dropship',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
