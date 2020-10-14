# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['celery_mock']

package_data = \
{'': ['*']}

install_requires = \
['celery>=5.0.0,<6.0.0']

setup_kwargs = {
    'name': 'celery-mock',
    'version': '1.1.6',
    'description': 'celery-mock allows you to mock celery task and run them when you want',
    'long_description': "===============================\nCelery Task Mocking\n===============================\n\n\n.. image:: https://img.shields.io/pypi/v/celery-mock.svg\n        :target: https://pypi.python.org/pypi/celery-mock\n\n.. image:: https://img.shields.io/travis/ulamlabs/celery-mock.svg\n        :target: https://travis-ci.org/ulamlabs/celery-mock\n\n.. image:: https://codecov.io/gh/ulamlabs/celery-mock/branch/master/graph/badge.svg\n  :target: https://codecov.io/gh/ulamlabs/celery-mock\n\n\ncelery-mock allows you to mock celery task and then run them when you want\n\nRationale\n==========\n\nSometimes a celery task retries itself to wait for some event or model to change.\nThis is hard to test because celery tasks run (and retry) inline in tests.\nNow you can choose when to run your tasks.\n\nSupported versions\n==================\n\n- Python 3 support\n- Celery 3.1.x and 4.0.x support \n\n\nHow to install\n================\n\n    .. code-block:: bash\n    \n        pip install celery-mock\n\n\nHow to use\n==========\n\n    .. code-block:: python\n    \n        from celery_mock import task_mock\n        from django.test import TestCase, Client\n        \n        from myapp import dummyview\n        \n        class UsersTestCase(TestCase):\n         \n            def test_create_user(self):\n                client = Client()\n                client.post('/api/users/', data={'username': 'konrad')  # runs tasks inline\n                \n                with task_mock():\n                    client.post('/api/users/', data={'username': 'konrad')\n                    # no tasks started yet\n                # all tasks ran here\n                \n                with task_mock('myapp.post_user_create_task'):\n                    client.post('/api/users/', data={'username': 'konrad')\n                    # all tasks started execept myapp.post_user_create_task\n                # myapp.post_user_create_task started here\n                \n                # you can use task_mock manually:\n                \n                tmock = task_mock().start()\n                client.post('/api/users/', data={'username': 'konrad')\n                # no tasks started yet\n                tomock.stop()  # all tasks ran here\n",
    'author': 'Konrad Rotkiewicz',
    'author_email': 'konrad@ulam.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ulamlabs/celery-mock/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
