# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['preql', 'preql.jup_kernel']

package_data = \
{'': ['*']}

install_requires = \
['dsnparse',
 'lark-parser>=0.10.0,<0.11.0',
 'prompt-toolkit',
 'pygments',
 'rich',
 'runtype>=0.1.4,<0.2.0',
 'tqdm']

extras_require = \
{'mysql': ['mysqlclient'], 'pgsql': ['psycopg2']}

entry_points = \
{'console_scripts': ['preql = preql.__main__:main']}

setup_kwargs = {
    'name': 'prql',
    'version': '0.1.7',
    'description': 'An interpreted relational query language that compiles to SQL',
    'long_description': '![alt text](logo_small.png "Logo")\n\nPreql (*pronounced: Prequel*) is an interpreted relational query language.\n\nIt is designed for use by data engineers, analyists and data scientists.\n\n* Preql compiles to SQL at runtime. It has the performance and abilities of SQL, and much more.\n\n* Programmer-friendly syntax and semantics, with gradual type-checking, inspired by Typescript and Python\n\n* Interface through Python, HTTP or a terminal environment with autocompletion\n\n* Escape hatch to SQL, for all those databse-specific features we didn\'t think to include\n\n* Support for Postgres, MySQL and Sqlite. (more planned!)\n\n(Preql is currently at the alpha stage, and isn\'t ready for production use yet)\n\n# Get started\n\nSimply install via pip:\n\n```bash\n    pip install -U prql\n```\n\nThen just run the interpeter:\n\n```bash\n    preql\n```\n\nRequires Python 3.8+\n\n# Documentation\n\n[Read here](https://preql.readthedocs.io/en/latest/)\n\n# Contributions\n\nCode contributions are welcome!\n\nBy submitting a contribution, you assign to Preql all right, title and interest in any copyright you have in the Contribution, and you waive any rights, including any moral rights, that may affect our ownership of the copyright in the Contribution.\n\n# License\n\nPreql uses an “Interface-Protection Clause” on top of the MIT license.\n\nSee: [LICENSE](LICENSE)\n\nIn simple words, it can be used for any commercial or non-commercial purpose, as long as your product doesn\'t base its value on exposing the Preql language itself to your users.\n\nIf you want to add the Preql language interface as a user-facing part of your commercial product, contact us for a commercial license.\n',
    'author': 'Erez Shin',
    'author_email': 'erezshin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/erezsh/Preql',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
