# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['django_icons', 'django_icons.renderers', 'django_icons.templatetags']

package_data = \
{'': ['*']}

install_requires = \
['django>=2.2,<4.0']

extras_require = \
{'docs': ['sphinx>=2.4,<3.0',
          'sphinx_rtd_theme>=0.4.3,<0.5.0',
          'm2r2>=0.2.5,<0.3.0']}

setup_kwargs = {
    'name': 'django-icons',
    'version': '2.2.0',
    'description': 'Icons for Django',
    'long_description': '# django-icons\n\nIcons for Django\n\n[![image](https://travis-ci.org/zostera/django-icons.svg?branch=main)](https://travis-ci.org/zostera/django-icons)\n[![image](https://coveralls.io/repos/github/zostera/django-icons/badge.svg?branch=main)](https://coveralls.io/github/zostera/django-icons?branch=main)\n[![Latest PyPI version](https://img.shields.io/pypi/v/django-icons.svg)](https://pypi.python.org/pypi/django-icons)\n[![Any color you like](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\n## Why should I use this?\n\n- Define your icons in your settings, with defaults for name, title and other attributes.\n- Generate icons using template tags.\n- Supports Font Awesome, Material, Bootstrap 3 and images out of the box.\n- Add other (custom) icon sets by subclassing a renderer.\n\n## How do I use this?\n\nDefine an icon in your `settings.py`, for example like this:\n\n```python\nDJANGO_ICONS = {\n    "ICONS": {\n        "edit": {"name": "far fa-pencil"},\n    },\n}\n```\nThe basic usage in a Django template:\n\n```djangotemplate\n{% load icons %}\n{% icon \'edit\' %}\n```\n\nThis will generate the FontAwesome 5 pencil icon in regular style:\n\n```html\n<i class="far fa-pencil"></i>\n```\n\nAdd extra classes and attributes to your predefined icon like this:\n\n```djangotemplate\n{% load icons %}\n{% icon \'edit\' extra_classes=\'fa-fw my-own-icon\' title=\'Update\' %}\n```\n\nThis will generate:\n\n```html\n<i class="far fa-pencil fa-fw my-own-icon" title="Update"></i>\n```\n\n## Requirements\n\nThis package requires a Python 3.6 or newer and Django 2.2 or newer.\n\nThe combination must be supported by the Django Project. See "Supported Versions" on <https://www.djangoproject.com/download/>.\n\n## Local installation\n\n`django-icons` adopts [Poetry](https://python-poetry.org) to manage its dependencies. This is the recommended way to do a local installation for development or to run the demo.\n\nAssuming Python>=3.6 is available on your system, the development dependencies are installed with Poetry as follows:\n\n```shell script\n$ git clone git://github.com/zostera/django-icons.git\n$ cd colour\n$ poetry install\n```\n\n### Running the demo\n\nYou can run the small demo app that is part of the test suite:\n\n```shell script\npoetry run python manage.py runserver\n```\n\n### Running the tests\n\nThe test suite requires [tox](https://tox.readthedocs.io/) to be installed. Run the complete test suite like this:\n\n```shell script\ntox\n```\n\nTest for the current (virtual) environment can be run with the Django `manage.py` command. If you need to do this, you will need to have an understanding of Python virtual environments. Explaining those is beyong the scope of this README.\n\n```shell script\npython manage.py test\n```\n\n## Origin\n\nOur plans at Zostera for an icon tool originate in <https://github.com/dyve/django-bootstrap3>. We isolated this into a Font Awesome tool in <https://github.com/zostera/django-fa>. When using our own product, we felt that the icon tool provided little improvement over plain HTML. Also, Font Awesome\'s icon names did not match the the intended function of the icon.\n\nThis is how we came to think of a library that:\n\n- Took a limited number of arguments\n- Converted those arguments into an icon\n- Was able to support multiple icon libraries\n- And could easily be extended by users\n\nThis is how we came to write and use `django-icons`.\n',
    'author': 'Dylan Verheul',
    'author_email': 'dylan@zostera.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zostera/django-icons',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
