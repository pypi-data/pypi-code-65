# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_s2s']

package_data = \
{'': ['*']}

install_requires = \
['aio-pika>=6.7.1,<7.0.0']

setup_kwargs = {
    'name': 'py-s2s',
    'version': '0.1.0',
    'description': 'Python service to service communication over rabbitmq ephemeral queues',
    'long_description': None,
    'author': 'Skyler Lewis',
    'author_email': 'skyler@hivewire.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
