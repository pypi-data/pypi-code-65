# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['async_email', 'async_email.email']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'async-email',
    'version': '0.1.0',
    'description': '',
    'long_description': '# django-async-email\n\n[![Actions Status](https://github.com/eltonplima/django-async-email/workflows/tox/badge.svg)](https://github.com/eltonplima/django-async-email/actions)\n[![Actions Status](https://github.com/eltonplima/django-async-email/workflows/flake8/badge.svg)](https://github.com/eltonplima/django-async-email/actions)\n\n```python\nEMAILS_TEMPLATES = {\n    "password_reset": {\n        "subject": "registration/password_set_subject.txt",\n        "body_html": "registration/password_set_email.html",\n        "body_txt": "registration/password_set_email.txt",\n    }\n}\n```\n\n# Important notes\n\nBe careful with the email configured on the settings.DEFAULT_FROM_EMAIL.\n\n> An invalid email on settings.DEFAULT_FROM_EMAIL will not allow your project to run\n\npython setup.py sdist bdist_wheel && pip uninstall -y django_async_email && python -m pip install dist/django_async_email-0.1.0-py2.py3-none-any.whl\n\n## Demo project\n\n```shell script\ncd demo_project\n# Build and run the docker image\ndocker-compose build && docker-compose up -d demo_project\n# Run migrations\ndocker-compose exec demo_project python manage.py migrate\n# Create the superuser\ndocker-compose exec demo_project python manage.py createsuperuser\n```\n\n```shell script\ncelery worker --app=demo_project.celery -l info --pool=eventlet\n```\n',
    'author': 'Elton Lima',
    'author_email': 'me@eltonplima.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/eltonplima/django-async-email',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
}


setup(**setup_kwargs)
