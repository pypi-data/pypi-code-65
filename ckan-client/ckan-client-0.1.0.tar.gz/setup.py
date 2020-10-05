# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ckanclient']

package_data = \
{'': ['*']}

modules = \
['License', 'README']
install_requires = \
['frictionless-ckan-mapper>=1.0.6,<2.0.0', 'requests>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'ckan-client',
    'version': '0.1.0',
    'description': 'CKAN Python SDK for CKAN3 instances with CKAN3 cloud storage.',
    'long_description': '<div align="center">\n\n# CKAN Client: Python SDK\n\n[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/datopian/ckan3-py-sdk/issues)\n[![ckan-client-py actions](https://github.com/datopian/ckan-client-py/workflows/ckan-client-py%20actions/badge.svg)](https://github.com/datopian/ckan-client-py/actions?query=workflow%3A%22ckan-client-py+actions%22)\n[![The MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](http://opensource.org/licenses/MIT)\n\nCKAN 3 SDK for CKAN instances with CKAN v3 style cloud storage.<br> This SDK will communicate with [`ckanext-authz-service`](https://github.com/datopian/ckanext-authz-service) (using CKAN to provide authorization tokens for other related systems) and [Giftless](https://github.com/datopian/giftless) (a highly customizable and extensible Git LFS server implemented in Python) to upload data to blob storage.\n\nRead more about [it\'s design](http://tech.datopian.com/blob-storage/#direct-to-cloud-upload).\n\n</div>\n\n## Install\n\nAll you need is [Git](https://git-scm.com/), and [Python](https://www.python.org/) 3.6+ with a [PEP 527](https://www.python.org/dev/peps/pep-0517/) compliant tool, such as [Poetry](https://python-poetry.org/).\n\nFirst, clone this repository:\n\n```console\n$ git clone https://github.com/datopian/ckan-client-py.git\n```\n\nThen, move to is directory:\n\n```console\n$ cd ckan-client-py\n```\nAnd install the package and its dependencies, for example, with Poetry:\n\n```console\n$ poetry install\n```\n\n## Usage\n\n### `ckanclient.Client`\n\nArguments:\n\n| Name           | Description       |\n| -------------- | ----------------- |\n| `api_url`      | CKAN API key      |\n| `api_key`      | CKAN instance URL |\n| `organization` | Organization      |\n| `dataset_id`   | Dataset id        |\n| `lfs_url`      | Git LFS URL       |\n\n\nExample:\n\n```python\nfrom ckanclient import Client\n\n\nclient = Client(\n    \'771a05ad-af90-4a70-beea-cbb050059e14\',\n    \'http://localhost:5000\',\n    \'datopian\',\n    \'dailyprices\',\n    \'http://localhost:9419\',\n)\n```\n\nThese settings matches the standard of [`ckanext-blob-storage`](https://github.com/datopian/ckanext-blob-storage) development environment, but you still need to create the user and organization there.\n\n###  `ckanclient.Client.action`\n\nArguments:\n\n| Name                 | Type       | Default    | Description                                                  |\n| -------------------- | ---------- | ---------- | ------------------------------------------------------------ |\n| `name`               | `str`      | (required) | The action name, for example, `site_read`, `package_show`…   |\n| `payload`            | `dict`     | (required) | The payload being sent to CKAN. If a payload is provided for a GET request, it will be converted to URL parameters and each key will be converted to snake case. |\n| `http_get`           | `bool`     | `False`    | Optional, if `True` will make `GET` request, otherwise `POST`. |\n| `transform_payload`  | `function` | `None`     | Function to mutate the `payload` before making the request (useful to convert to and from CKAN and Frictionless formats). |\n| `transform_response` | `function` | `None`     | function to mutate the response data before returning it (useful to convert to and from CKAN and Frictionless formats). |\n\nThis method is used internally by the following methods.\n\n### `ckanclient.Client.create`\n\nArguments:\n\n| Name                       | Type            | Description                                                  |\n| -------------------------- | --------------- | ------------------------------------------------------------ |\n| `dataset_name_or_metadata` | `str` or `dict` | It is either a string being a valid dataset name or dictionary with meta-data for the dataset in Frictionless format. |\n\nExample:\n\n```python\ndataset = client.create(\'dailyprices\')\n```\n\n### `ckanclient.Client.push`\n\nArguments:\n\n| Name               | Type   | Description                               |\n| ------------------ | ------ | ----------------------------------------- |\n| `dataset_metadata` | `dict` | Dataset meta-data in Frictionless format. |\n\nExample:\n\n```python\ndataset_metadata = {\n    \'id\': \'16d6e8d7-a848-48b1-91d0-fd393c1c6c01\',\n    \'name\': \'dailyprices\',\n    \'owner_org\': \'57f97769-a982-4ccd-91f0-1d86dee822e3\',\n    \'title\': \'dailyprices\',\n    \'type\': \'dataset\',\n    \'contributors\': [],\n    # …\n}\ndataset = client.push(dataset_metadata)\n```\n\n###  `ckanclient.Client.retrieve`\n\nArguments:\n\n| Name         | Type  | Description                |\n| ------------ | ----- | -------------------------- |\n| `name_or_id` | `str` | Id or name of the dataset. |\n\nExample:\n\n```python\ndataset = client.retrieve(\'dailyprices\')\n```\n\n### `ckanclient.Client.push_blob`\n\nArguments:\n\n| Name       | Type   | Description              |\n| ---------- | ------ | ------------------------ |\n| `resource` | `dict` | A Frictionless resource. |\n\n\n## Tests\n\nTo run tests:\n\n```console\n$ poetry run pytest\n```\n\n## License\n\nThis project is licensed under the MIT License - see the [LICENSE](License) file for details\n',
    'author': 'Datopian',
    'author_email': 'contact@datopian.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/datopian/ckan-client-py',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
