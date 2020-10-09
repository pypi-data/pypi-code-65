# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_dramatiq_email']

package_data = \
{'': ['*']}

install_requires = \
['django<3.0',
 'django_dramatiq>=0.9.1,<0.10.0',
 'dramatiq>=1.8.1,<2.0.0',
 'pika>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'django-dramatiq-email',
    'version': '1.0.0',
    'description': 'A Django email backend using Dramatiq to send emails using background workers',
    'long_description': None,
    'author': 'Tim Drijvers',
    'author_email': 'tim@sendcloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sendcloud/django-dramatiq-email',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
