# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['jsonschema2ddl']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.3.19,<2.0.0',
 'change_case>=0.5.2,<0.6.0',
 'iso8601>=0.1.12,<0.2.0',
 'psycopg2>=2.8.6,<3.0.0']

entry_points = \
{'console_scripts': ['vscode = scripts.setup:vscode']}

setup_kwargs = {
    'name': 'jsonschema2ddl',
    'version': '0.0.2',
    'description': 'Generate Database tables from JSON schema',
    'long_description': None,
    'author': 'Pablo San José',
    'author_email': 'pablo.sanjose@clarity.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
