# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ptonppl']

package_data = \
{'': ['*']}

install_requires = \
['python-ldap>=3.3.1,<4.0.0']

setup_kwargs = {
    'name': 'ptonppl',
    'version': '0.0.1',
    'description': 'An integration package to lookup Princeton campus users.',
    'long_description': '# ptonppl\nAn integration package to lookup Princeton campus users.\n',
    'author': 'Jérémie Lumbroso',
    'author_email': 'lumbroso@cs.princeton.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jlumbroso/ptonppl',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
