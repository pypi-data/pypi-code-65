# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bigbluebutton',
 'bigbluebutton.api',
 'bigbluebutton.cli',
 'bigbluebutton.django',
 'bigbluebutton.django.migrations']

package_data = \
{'': ['*']}

install_requires = \
['click-log>=0.3.2,<0.4.0',
 'defusedxml>=0.6.0,<0.7.0',
 'inflection>=0.5.0,<0.6.0',
 'requests>=2.23.0,<3.0.0',
 'xmltodict>=0.12.0,<0.13.0']

extras_require = \
{'caching': ['ucache>=0.1.4,<0.2.0', 'peewee>=3.13.3,<4.0.0'],
 'cli': ['click>=7.1.1,<8.0.0',
         'toml>=0.10.0,<0.11.0',
         'tabulate>=0.8.7,<0.9.0'],
 'django': ['django>=3.0.6,<4.0.0', 'dicttoxml>=1.7.4,<2.0.0'],
 'sysstat': ['sadf>=0.1.2,<0.2.0']}

entry_points = \
{'console_scripts': ['bbb-cli = bigbluebutton.cli:bbb']}

setup_kwargs = {
    'name': 'bigbluebutton2',
    'version': '0.1a2',
    'description': 'Sophisticated Python client library for BigBlueButton™ with Django integration',
    'long_description': 'BigBlueButton™ API implementation for Python\n============================================\n\nSynopsis\n--------\n\nbigbluebutton2 is a sophisticated Python client library for BigBlueButton™\nwith Django integration.\n\nThis package implements tools for using the API of the\n`BigBlueButton`_ web conferencing and online teaching software. In order to\nbroadly support the software in widespread python-based ecosystems, it\ncontains:\n\n* an object-oriented library wrapping the `XML-RPC API`_\n* a multi-server capable container that transparently wraps BigBlueButton\n  server clusters, including load-balancing\n* a command-line interface (CLI) tool to manage BigBlueButton (including\n  clusters)\n* an integration app for the `Django`_ web framework, including an\n  API proxy view with multi-tenant/scoping support\n\nThe project serves as the core for `InfraBlue`_, the django-based material\ndesign BigBlueButton frontend, and the conferencing integration in the\n`AlekSIS`_ school information system.\n\n\nDocumentation\n-------------\n\nFor an overview of all features of the different parts of\npython-bigbluebutton2, as well as a complete API reference, please refer to\nthe `full documentation`_.\n\n\nLicense\n-------\n\nThis library is free and open software, licensed under the terms of the MIT\nlicense. See the LICENSE file for details.\n\n\n.. _BigBlueButton: https://bigbluebutton.org/\n.. _XML-RPC API: https://docs.bigbluebutton.org/dev/api.html\n.. _Django: https://www.djangoproject.com/\n.. _InfraBlue: https://edugit.org/infrablue/infrablue\n.. _AlekSIS: https://aleksis.org/\n.. _full documentation: https://infrablue.edugit.io/python-bigbluebutton2/docs/html/\n',
    'author': 'Dominik George',
    'author_email': 'dominik.george@teckids.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://infrablue.edugit.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
