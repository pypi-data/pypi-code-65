# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['netscud',
 'netscud.devices',
 'netscud.devices.alcatel',
 'netscud.devices.cisco']

package_data = \
{'': ['*']}

install_requires = \
['asyncssh>=2.4.2,<3.0.0', 'pyyaml>=5.3.1,<6.0.0']

setup_kwargs = {
    'name': 'netscud',
    'version': '1.0.0',
    'description': 'Network device Asynchronous python library',
    'long_description': None,
    'author': 'ericorain',
    'author_email': 'ericorain@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
