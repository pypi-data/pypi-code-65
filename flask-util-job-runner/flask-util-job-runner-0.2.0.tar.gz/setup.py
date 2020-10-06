# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flask_util_job_runner']

package_data = \
{'': ['*']}

install_requires = \
['Flask==1.1.2',
 'gunicorn==20.0.4',
 'minio==6.0.0',
 'redis==3.5.3',
 'requests==2.24.0']

setup_kwargs = {
    'name': 'flask-util-job-runner',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'eqqe',
    'author_email': 'sfbrey@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
