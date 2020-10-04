# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['databricksbundle']

package_data = \
{'': ['*'],
 'databricksbundle': ['_config/*',
                      'container/*',
                      'dbutils/*',
                      'jdbc/*',
                      'notebook/*',
                      'pipeline/decorator/*',
                      'pipeline/decorator/executor/*',
                      'pipeline/function/*',
                      'pipeline/function/service/*',
                      'spark/*',
                      'spark/config/*']}

install_requires = \
['injecta>=0.8.9,<0.9.0',
 'ipython>=7.0.0,<8.0.0',
 'logger-bundle>=0.5.0,<0.6.0',
 'pandas>=0.24.2',
 'pyarrow>=0.16.0,<0.17.0',
 'pyfony-bundles>=0.2.0,<0.3.0']

setup_kwargs = {
    'name': 'databricks-bundle',
    'version': '0.5.7b3',
    'description': 'Databricks bundle for the Pyfony framework',
    'long_description': 'Databricks bundle for the Pyfony framework\n',
    'author': 'Jiri Koutny',
    'author_email': 'jiri.koutny@datasentics.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bricksflow/databricks-bundle',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<3.8.0',
}


setup(**setup_kwargs)
