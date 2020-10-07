# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['abilian',
 'abilian.crm',
 'abilian.crm.excel',
 'abilian.crm.excel.columns',
 'abilian.crm.generator',
 'abilian.crm.generator.fieldtypes',
 'abilian.crm.tests']

package_data = \
{'': ['*'],
 'abilian.crm': ['static/js/*',
                 'templates/crm/excel/*',
                 'templates/crm/widgets/*',
                 'translations/*',
                 'translations/en/LC_MESSAGES/messages.po',
                 'translations/fr/LC_MESSAGES/messages.po']}

install_requires = \
['abilian-core<0.11',
 'more-itertools<6',
 'numpy',
 'openpyxl>=2.3.3',
 'pandas',
 'phonenumbers>=7.1.0',
 'werkzeug<1']

setup_kwargs = {
    'name': 'abilian-crm-core',
    'version': '0.1.28',
    'description': 'Core framework for CRM applications',
    'long_description': None,
    'author': 'Stefane Fermigier',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/abilian/abilian-crm-core',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>3.6.1,<4',
}


setup(**setup_kwargs)
