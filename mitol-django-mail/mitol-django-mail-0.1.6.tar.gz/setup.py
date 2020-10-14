# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mitol', 'mitol.mail']

package_data = \
{'': ['*'], 'mitol.mail': ['templates/mail/*', 'templates/mail/partials/*']}

install_requires = \
['Django>=2.2.12,<3.0.0',
 'beautifulsoup4>=4.6.0,<5.0.0',
 'django-anymail>=6.1,<9.0',
 'html5lib>=1.1,<2.0',
 'premailer>=3.7.0,<4.0.0',
 'toolz>=0.9.0,<0.11.0']

setup_kwargs = {
    'name': 'mitol-django-mail',
    'version': '0.1.6',
    'description': 'MIT Open Learning django app extensions for mail',
    'long_description': None,
    'author': 'MIT Office of Open Learning',
    'author_email': 'mitx-devops@mit.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<3.9',
}


setup(**setup_kwargs)
