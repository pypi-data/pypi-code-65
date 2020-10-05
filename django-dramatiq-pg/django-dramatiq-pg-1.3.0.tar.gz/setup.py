# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['django_dramatiq_pg', 'django_dramatiq_pg.migrations']

package_data = \
{'': ['*']}

install_requires = \
['django>=3.1', 'dramatiq-pg>=0.9.0']

setup_kwargs = {
    'name': 'django-dramatiq-pg',
    'version': '1.3.0',
    'description': 'Integration of Django with dramatiq-pg',
    'long_description': '==================\ndjango_dramatiq_pg\n==================\n\n.. image:: https://badge.fury.io/py/django-dramatiq-pg.svg\n    :target: https://pypi.org/project/django-dramatiq-pg\n\n.. image:: https://img.shields.io/pypi/pyversions/django-dramatiq-pg.svg\n    :target: https://pypi.org/project/django-dramatiq-pg\n\ndramatiq-pg_ integration for django_.\n\n    .. _dramatiq-pg: https://pypi.org/project/dramatiq-pg/\n    .. _django: https://pypi.org/project/Django/\n\nInstallation\n------------\n\n1. Install with pip\n\n   .. code-block:: sh\n\n    $ pip install django-dramatiq-pg\n\n2. Add to your ``INSTALLED_APPS`` list in settings.py\n\n   .. code-block:: python\n\n    INSTALLED_APPS = [\n        ...\n        \'django_dramatiq_pg\',\n    ]\n\n3. Create a Registry, and register your tasks\n\n   .. code-block:: python\n\n     from django_dramatiq_pg.registry import Registry\n\n     tasks = Registry()\n\n\n     @tasks.actor\n     def mytask():\n         ...\n\n4. Configure\n\n   .. code-block:: python\n\n    DRAMATIQ_BROKER = {\n        "OPTIONS": {\n            "url": "postgres:///mydb",\n        },\n        "MIDDLEWARE": [\n            "dramatiq.middleware.TimeLimit",\n            "dramatiq.middleware.Callbacks",\n            "dramatiq.middleware.Retries",\n        ],\n    }\n    DRAMATIQ_REGISTRY = \'myapp.registry.tasks\'\n\n5. Start the worker process:\n\n   .. code-block:: sh\n\n    $ dramatiq django_dramatiq_pg.worker\n\nThis worker module will auto-discover any module called \'actors\' in\n``INSTALLED_APPS``.\n\nRegistry\n========\n\nIn a typical `dramatiq` application, the `Broker` is configured before any\ntasks are registered. However, as `Django` is in control of the intialisation\nsequence, there is an issue of ordering; the `actor` decorator assumes the\nbroker is already configured.\n\nTo resolve this, `django_dramatiq_pg` provides a `Registry` for your tasks,\nwhich is then bound to the `Broker` when Django initialises.\n\nIn your code, declare a `Registry` instance, and use its `.actor` method to\ndecorate your task functions. Then tell `django_dramatiq_pg` to use your\nregistry with the `DRAMATIQ_REGISTRY` setting.\n\nIf you do not specify one, `django_dramatiq_pg` will create one on start.\n\nThe registry can be accessed as the `.registry` attribute on the\n`django_dramatiq_pg` App instance.\n\nSettings\n--------\n\nDRAMATIQ_BROKER\n  A dict of options to pass when instantiating the broker.\n\nDRAMATIC_BROKER[\'OPTIONS\']\n  Arguments to pass to the Broker.\n\nDRAMATIC_BROKER[\'MIDDLEWARE\']\n  A list of middleware classes to be passed to the broker.\n\n  These can either be import strings, or instances.\n\nDRAMATIQ_ENCODER\n  Default: None\n\n  Import path for encoder class.\n\nDRAMATIQ_ACTORS_MODULE\n  Default: \'actors\'\n\n  Name of module use to auto-discover actors in INSTALLED_APPS.\n\nDRAMATIQ_REGISTRY\n\n  Import path for the task Registry instance.\n\n  This should refer to an instance of `django_dramatiq_pg.registry.Registry`.\n\n  This resolves the chicken/egg problem of declaring tasks before the broker is\n  configured.\n',
    'author': 'Curtis Maloney',
    'author_email': 'curtis@tinbrain.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/uptick/django-dramatiq-pg',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
