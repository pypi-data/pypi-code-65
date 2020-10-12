# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ephios',
 'ephios.event_management',
 'ephios.event_management.migrations',
 'ephios.event_management.templatetags',
 'ephios.extra',
 'ephios.extra.management',
 'ephios.extra.management.commands',
 'ephios.extra.templatetags',
 'ephios.plugins',
 'ephios.plugins.basesignup',
 'ephios.plugins.basesignup.signup',
 'ephios.plugins.pages',
 'ephios.plugins.pages.migrations',
 'ephios.user_management',
 'ephios.user_management.migrations']

package_data = \
{'': ['*'],
 'ephios': ['locale/de/LC_MESSAGES/django.po',
            'static/bootstrap/css/*',
            'static/bootstrap/js/*',
            'static/datatables/*',
            'static/datatables/DataTables-1.10.21/css/*',
            'static/datatables/DataTables-1.10.21/images/*',
            'static/datatables/DataTables-1.10.21/js/*',
            'static/datatables/Responsive-2.2.5/css/*',
            'static/datatables/Responsive-2.2.5/js/*',
            'static/ephios/css/*',
            'static/ephios/js/*',
            'static/fontawesome/css/*',
            'static/fontawesome/webfonts/*',
            'static/select2/css/*',
            'static/select2/js/*',
            'static/select2/js/i18n/*',
            'static/sortablejs/*',
            'templates/*',
            'templates/registration/*'],
 'ephios.event_management': ['templates/event_management/*',
                             'templates/event_management/fragments/*',
                             'templates/event_management/mails/*'],
 'ephios.plugins.basesignup': ['templates/basesignup/*',
                               'templates/basesignup/requestconfirm_signup/*'],
 'ephios.plugins.pages': ['templates/pages/*'],
 'ephios.user_management': ['templates/user_management/*']}

install_requires = \
['bleach>=3.2.1,<4.0.0',
 'django-bootstrap4>=2.2.0,<3.0.0',
 'django-csp>=3.7,<4.0',
 'django-environ>=0.4.5,<0.5.0',
 'django-formset-js-improved>=0.5.0,<0.6.0',
 'django-guardian>=2.3.0,<3.0.0',
 'django-ical>=1.7.1,<2.0.0',
 'django-polymorphic>=3.0.0,<4.0.0',
 'django-select2>=7.4.2,<8.0.0',
 'django>=3.1,<4.0',
 'markdown>=3.2.2,<4.0.0',
 'reportlab>=3.5.51,<4.0.0']

extras_require = \
{'mysql': ['mysqlclient>=2.0.1,<3.0.0'], 'pgsql': ['psycopg2>=2.8.6,<3.0.0']}

setup_kwargs = {
    'name': 'ephios',
    'version': '0.1.4',
    'description': 'ephios is a tool to manage shifts for medical services.',
    'long_description': '![ephios](https://github.com/ephios-dev/ephios/workflows/ephios/badge.svg)\n# ephios\nephios is a tool to manage shifts for medical services.\n\n## Development setup\n\nTo set up a development version on your local machine, you need to execute the following steps:\n1. Check out repository and cd to it\n2. Set up a virtualenv for the project with Python >=3.8 and activate it\n3. Install poetry (if not already installed): `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python`\n4. Install dependencies with `poetry install`\n5. Create env file with `cp .env.example .env`\n6. Migrate the database with `python manage.py migrate`\n7. Compile translations with `python manage.py compilemessages`\n8. Load data for testing with `python manage.py setupdata debug`\n9. Start the development server with `python manage.py runserver`\n10. Open your web browser, visit `http://localhost:8000` and log in with the default credentials (user `admin@localhost` and password `admin`)\n\nBefore committing, make sure to lint your changes with `black .`. You can also check the [IDE integration](https://github.com/psf/black#editor-integration) or install a pre-commit hook with `pre-commit install` (recommended). You also need to to test the code with `pytest`.\n',
    'author': 'Julian Baumann',
    'author_email': 'julian@ephios.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://ephios.de',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
