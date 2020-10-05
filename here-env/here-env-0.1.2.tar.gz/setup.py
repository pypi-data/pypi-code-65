# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['here_env']
install_requires = \
['click>=7.1.2,<8.0.0']

entry_points = \
{'console_scripts': ['here-env = here_env:cli']}

setup_kwargs = {
    'name': 'here-env',
    'version': '0.1.2',
    'description': 'Small helper to create and active virtuel environments.',
    'long_description': "# here-env\n\nSmall helper to create and active virtuel environments.\n\n## Usage\n\n```sh\neval $(here-env)\n```\n\nThis will create a venv in `$PWD/.venv` or in `$GIT_ROOT/.venv` (if currently\nin a Git repository) and activate it.\n\nYou can also create a simple `here` shell alias:\n\n```sh\nalias here='eval $(here-env)'\n```\n",
    'author': 'Simon Westphahl',
    'author_email': 'simon@westphahl.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
