# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['django_sysinfo', 'django_sysinfo.templatetags']

package_data = \
{'': ['*'],
 'django_sysinfo': ['static/sysinfo/*', 'templates/admin/sysinfo/*']}

install_requires = \
['psutil', 'pytz>=2020.1,<2021.0']

setup_kwargs = {
    'name': 'django-sysinfo',
    'version': '2.0.0',
    'description': 'Simple django app to expose system infos: libraries version, databae server infos...',
    'long_description': None,
    'author': 'sax',
    'author_email': 's.apostolico@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
