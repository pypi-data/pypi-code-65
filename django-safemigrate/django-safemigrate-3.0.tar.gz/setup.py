# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['django_safemigrate',
 'django_safemigrate.management',
 'django_safemigrate.management.commands']

package_data = \
{'': ['*']}

install_requires = \
['django>=3.0,<4.0']

setup_kwargs = {
    'name': 'django-safemigrate',
    'version': '3.0',
    'description': 'Safely run migrations before deployment',
    'long_description': '===========================================================\ndjango-safemigrate: Safely run migrations before deployment\n===========================================================\n\n.. image:: https://img.shields.io/pypi/v/django-safemigrate.svg\n   :target: https://pypi.org/project/django-safemigrate/\n   :alt: Latest Version\n\n.. image:: https://dev.azure.com/aspiredu/django-safemigrate/_apis/build/status/1?branchName=master\n   :target: https://dev.azure.com/aspiredu/django-safemigrate/_build/latest?definitionId=1&branchName=master\n   :alt: Build status\n\n.. image:: https://codecov.io/gh/aspiredu/django-safemigrate/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/aspiredu/django-safemigrate\n   :alt: Code Coverage\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/ambv/black\n   :alt: Code style: black\n\n|\n\ndjango-safemigrate adds a ``safemigrate`` command to Django\nto allow for safely running a migration command when deploying.\n\nUsage\n=====\n\nInstall ``django-safemigrate``, then add this to the\n``INSTALLED_APPS`` in the settings file:\n\n.. code-block:: python\n\n    INSTALLED_APPS = [\n        # ...\n        "django_safemigrate.apps.SafeMigrateConfig",\n    ]\n\nThen mark any migration that may be run\nduring a pre-deployment stage,\nsuch as a migration to add a column.\n\n.. code-block:: python\n\n    from django_safemigrate import Safe\n\n    class Migration(migrations.Migration):\n        safe = Safe.before_deploy\n\nAt this point you can run the ``safemigrate`` Django command\nto run the migrations, and only these migrations will run.\nHowever, if migrations that are not safe to run before\nthe code is deployed are dependencies of this migration,\nthen these migrations will be blocked, and the safemigrate\ncommand will fail with an error.\n\nWhen the code is fully deployed, just run the normal ``migrate``\nDjango command, which still functions normally.\nFor example, you could add the command to the release phase\nfor your Heroku app, and the safe migrations will be run\nautomatically when the new release is promoted.\n\nSafety Options\n==============\n\nThere are three options for the value of the\n``safe`` property of the migration.\n\n* ``Safe.before_deploy``\n\n  This migration is only safe to run before the code change is deployed.\n  For example, a migration that adds a new field to a model.\n\n* ``Safe.after_deploy``\n\n  This migration is only safe to run after the code change is deployed.\n  This is the default that is applied if no ``safe`` property is given.\n  For example, a migration that removes a field from a model.\n\n* ``Safe.always``\n\n  This migration is safe to run before *and* after\n  the code change is deployed.\n  For example, a migration that changes the ``help_text`` of a field.\n\nNonstrict Mode\n==============\n\nUnder normal operation, if there are migrations\nthat must run before the deployment that depend\non any migration that is marked to run after deployment\n(or is not marked),\nthe command will raise an error to indicate\nthat there are protected migrations that\nshould have already been run, but have not been,\nand are blocking migrations that are expected to run.\n\nIn development, however, it is common that these\nwould accumulate between developers,\nand since it is acceptable for there to be downtime\nduring the transitional period in development,\nit is better to allow the command to continue without raising.\n\nTo enable nonstrict mode, add the ``SAFEMIGRATE`` setting:\n\n.. code-block:: python\n\n    SAFEMIGRATE = "nonstrict"\n\nIn this mode ``safemigrate`` will run all the migrations\nthat are not blocked by any unsafe migrations.\nAny remaining migrations can be run after the fact\nusing the normal ``migrate`` Django command.\n',
    'author': 'Ryan Hiebert',
    'author_email': 'ryan@aspiredu.com',
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
