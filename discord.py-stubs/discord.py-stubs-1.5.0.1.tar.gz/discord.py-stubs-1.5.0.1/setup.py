# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['discord-stubs']

package_data = \
{'': ['*'], 'discord-stubs': ['ext/commands/*', 'ext/tasks/*']}

install_requires = \
['mypy>=0.782', 'typing-extensions>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'discord.py-stubs',
    'version': '1.5.0.1',
    'description': 'discord.py stubs',
    'long_description': '# discord.py-stubs\n\n[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://github.com/bryanforbes/discord.py-stubs/blob/master/LICENSE)\n[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\nThis package contains type stubs to provide more precise static types and type inference for discord.py.\n\n## Installation\n\n```\npip install discord.py-stubs\n```\n\n**NOTE:** Because `discord.py` uses namespace packages for its extensions, `mypy` must be configured to use namespace packages either with the `--namespace-packages` command line flag, or by setting `namespace_packages = True` in your `mypy` configuration file. See the [import discovery](https://mypy.readthedocs.io/en/stable/command_line.html#import-discovery) section of the `mypy` documentation for more details.\n\n## Usage Notes\n\nIn most cases, installing this package will enable developers to type check their discord.py bots using mypy out of the box. However, if developers wish to subclass the classes in `discord.ext.commands` they will need to follow the `mypy` documentation outlining how to use [classes that are generic in stubs but not at runtime](https://mypy.readthedocs.io/en/stable/common_issues.html#using-classes-that-are-generic-in-stubs-but-not-at-runtime):\n\n```python\nfrom typing import TYPE_CHECKING\nfrom discord.ext import commands\n\nclass MyContext(commands.Context):\n    ...\n\nif TYPE_CHECKING:\n    Cog = commands.Cog[MyContext]\nelse:\n    Cog = commands.Cog\n\nclass MyCog(Cog):\n    ...\n```\n\nIn order to avoid this issue, developers can use [`discord-ext-typed-commands`](https://github.com/bryanforbes/discord-ext-typed-commands/):\n\n```python\nfrom discord.ext import typed_commands\n\nclass MyContext(typed_commands.Context):\n    ...\n\nclass MyCog(typed_commands.Cog[MyContext]):\n    ...\n```\n\n## Development\n\nMake sure you have [poetry](https://python-poetry.org/) installed.\n\n```\npoetry install\npoetry run pre-commit install --hook-type pre-commit --hook-type post-checkout\n```\n\n\n## Version numbering scheme\n\nAt this time, the version number of `discord.py-stubs` will follow the version number of `discord.py` it corresponds to and append one more version segment that indicates the sequence of releases for the stubs. For instance, if you are using `discord.py` version `1.3.4`, you would use `discord.py-stubs` version `1.3.4.X` where `X` is an integer.\n',
    'author': 'Bryan Forbes',
    'author_email': 'bryan@reigndropsfall.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bryanforbes/discord.py-stubs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
