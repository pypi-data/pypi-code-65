# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flask_firebase_admin']

package_data = \
{'': ['*']}

install_requires = \
['firebase-admin>=4.0.0,<5.0.0', 'flask>=1.0.0,<2.0.0']

setup_kwargs = {
    'name': 'flask-firebase-admin',
    'version': '0.1.0',
    'description': 'Firebase for Flask',
    'long_description': None,
    'author': 'Andrew Ross',
    'author_email': 'andrew.ross.mail@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
