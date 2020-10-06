# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['django_sftp',
 'django_sftp.management',
 'django_sftp.management.commands',
 'django_sftp.migrations']

package_data = \
{'': ['*']}

install_requires = \
['asyncssh>=2.4.2,<3.0.0', 'click>=7.0,<8.0']

entry_points = \
{'console_scripts': ['django-sftp = django_sftp.__main__:main']}

setup_kwargs = {
    'name': 'django-sftp',
    'version': '0.2.1',
    'description': 'Django SFTP',
    'long_description': '\nDjango SFTP [WIP]\n===========\n\n\n[![Tests](https://github.com/vahaah/django-sftp/workflows/Tests/badge.svg)](https://github.com/vahaah/django-sftp/actions?workflow=Tests)\n[![Codecov](https://codecov.io/gh/vahaah/django-sftp/branch/master/graph/badge.svg)](https://codecov.io/gh/vahaah/django-sftp)\n[![PyPI](https://img.shields.io/pypi/v/django-sftp.svg)](https://pypi.org/project/django-sftp/)\n[![Python Version](https://img.shields.io/pypi/pyversions/django-sftp)](https://pypi.org/project/django-sftp/)\n[![Read the Docs](https://readthedocs.org/projects/django-sftp/badge/)](https://django-sftp.readthedocs.io/)\n[![License](https://img.shields.io/pypi/l/django-sftp)](https://opensource.org/licenses/MIT)\n[![License](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n[![Dependabot](https://api.dependabot.com/badges/status?host=github&repo=vahaah/django-sftp)](https://dependabot.com)\n\n\nFeatures\n--------\n\n* TODO\n\n\nRequirements\n------------\n\n* TODO\n\n\nGetting Started\n---------------\n\n1.  Install django-sftp by pip.\n```bash\n$ pip install django-sftp\n```\n\n2. Add it to your `INSTALLED_APPS`:\n```python\nINSTALLED_APPS = (\n   ...\n   \'django_sftp\',\n   ...\n)\n```\n\n3. Migrate app.\n```bash\n$ ./manage.py migrate\n```\n\n4. Create user account.\n```bash\n$ ./manage.py createsuperuser --username user\n```\n\n5. Create SFTP user group.\n```bash\n$ ./manage.py createsftpusergroup test\n```\n\n6. Create SFTP account.\n```bash\n$ ./manage.py createftpuseraccount user test\n```\n\n7. Generate RSA key\n```bash\n$ ssh-keygen -t rsa -b 4096 -C "your_email@example.com" -m PEM\n```\n\n8. Run SFTP server\n```bash\n$ ./manage.py sftpserver :11121 -k rsa\n```\n\nUsage\n-----\n\n* TODO\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`.\n\n\nLicense\n-------\n\nDistributed under the terms of the MIT_ license,\n*Django SFTP* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue` along with a detailed description.\n\n\nCredits\n-------\n\n* MIT: http://opensource.org/licenses/MIT\n* file an issue: https://github.com/vahaah/django-sftp/issues\n* pip: https://pip.pypa.io/\n* Contributor Guide: CONTRIBUTING.rst\n',
    'author': 'Alex Vakhitov',
    'author_email': 'alex@vakhitov.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vahaah/django-sftp',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0.0',
}


setup(**setup_kwargs)
