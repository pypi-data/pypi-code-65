# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['django_cloudtask',
 'django_cloudtask.management',
 'django_cloudtask.management.commands']

package_data = \
{'': ['*']}

install_requires = \
['django-structlog>=1.5.2,<2.0.0',
 'django>=2.2.12,<3.0.0',
 'google-api-core>=1.14.2,<2.0.0',
 'google-cloud-scheduler>=1.3.0,<2.0.0',
 'google-cloud-tasks>=1.5.0,<2.0.0',
 'structlog>=20.1.0,<21.0.0']

setup_kwargs = {
    'name': 'django-cloudtask',
    'version': '0.1.4',
    'description': 'A django package for managing long running tasks using GCP Cloud Task',
    'long_description': '# django-cloudtask\nA django package for managing long running tasks via Cloud Run and Cloud Scheduler\n\n[![CircleCI](https://circleci.com/gh/kogan/django-cloudtask.svg?style=svg)](https://circleci.com/gh/kogan/django-cloudtask)\n\n## Should I be using this package?\n\nProbably not.\n\n## Configuration\n\nMake sure these are in your django settings:\n\n - `PROJECT_ID`\n   - the GCP project\n - `PROJECT_REGION`\n   - GCP region\n - `TASK_SERVICE_ACCOUNT`\n   - Service account which will be authenticated against\n - `TASK_DOMAIN`\n   - domain which receives tasks (cloud run)\n - `TASK_DEFAULT_QUEUE`\n   - default queue tasks will be added to\n\n## Contributing\n\nWe use `pre-commit <https://pre-commit.com/>` to enforce our code style rules\nlocally before you commit them into git. Once you install the pre-commit library\n(locally via pip is fine), just install the hooks::\n\n    pre-commit install -f --install-hooks\n\nThe same checks are executed on the build server, so skipping the local linting\n(with `git commit --no-verify`) will only result in a failed test build.\n\nCurrent style checking tools:\n\n- flake8: python linting\n- isort: python import sorting\n- black: python code formatting\n\nNote:\n\n    You must have python3.6 available on your path, as it is required for some\n    of the hooks.\n',
    'author': 'Alec McGavin',
    'author_email': 'alec.mcgavin@kogan.com.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://github.com/kogan/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
