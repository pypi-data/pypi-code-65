# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['infrablue',
 'infrablue.migrations',
 'infrablue.templatetags',
 'infrablue.util']

package_data = \
{'': ['*'],
 'infrablue': ['static/*',
               'static/img/*',
               'static/js/*',
               'templates/components/*',
               'templates/django_registration/*',
               'templates/dynamic_preferences/*',
               'templates/infrablue/*',
               'templates/infrablue/snippets/*',
               'templates/material/*',
               'templates/two_factor/*',
               'templates/two_factor/core/*',
               'templates/two_factor/profile/*']}

install_requires = \
['Django<3.2',
 'bigbluebutton2[django,sysstat]>=0.1a8,<0.2',
 'colour>=0.1.5,<0.2.0',
 'django-dynamic-preferences>=1.9,<2.0',
 'django-guardian>=2.3.0,<3.0.0',
 'django-material>=1.6.3,<2.0.0',
 'django-registration>=3.1,<4.0',
 'django-two-factor-auth[yubikey,phonenumbers,call,sms]>=1.11.0,<2.0.0',
 'django-yarnpkg>=6.0.1,<7.0.0',
 'django_any_js>=1.0.3,<2.0.0',
 'django_favicon_plus_reloaded>=1.0.4,<2.0.0',
 'django_menu_generator>=1.0.4,<2.0.0',
 'django_sass_processor>=0.8,<0.9',
 'dynaconf>=2.2.3,<3.0.0',
 'libsass>=0.20.0,<0.21.0',
 'psycopg2>=2.8.5,<3.0.0',
 'python-memcached>=1.59,<2.0']

extras_require = \
{'ldap': ['django-auth-ldap>=2.1.1,<3.0.0'],
 'social': ['social-auth-app-django>=4.0.0,<5.0.0']}

setup_kwargs = {
    'name': 'infrablue',
    'version': '0.1.0a1',
    'description': 'Material design frontend and server manager for BigBlueButton',
    'long_description': None,
    'author': 'Dominik George',
    'author_email': 'dominik.george@teckids.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://edugit.org/nik/infrablue',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
