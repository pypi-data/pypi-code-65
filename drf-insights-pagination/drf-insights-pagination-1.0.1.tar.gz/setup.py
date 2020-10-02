# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['drf_insights_pagination']

package_data = \
{'': ['*']}

install_requires = \
['djangorestframework']

setup_kwargs = {
    'name': 'drf-insights-pagination',
    'version': '1.0.1',
    'description': 'Provides pagination class that adheres to Insights IPP-12.',
    'long_description': "# DRF Insights Pagination\n\nA simple library to add a paginator to DRF that follows Insights IPP-12.\n\n### Installation and Usage\n\nInstall the library\n\n```\npip install drf-insights-pagination\n```\n\nChange your pagination class, and optionally `APP_PATH` in your settings\n\n```\nREST_FRAMEWORK = {\n    'DEFAULT_PAGINATION_CLASS': 'drf_insights_pagination.pagination.InsightsPagination',\n}\nINSIGHTS_PAGINATION_APP_PATH = '/api/application'\n```\n\n",
    'author': 'Cloudigrade Dev Team',
    'author_email': 'doppler-dev@redhat.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/cloudigrade/libraries/drf-insights-pagination',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
