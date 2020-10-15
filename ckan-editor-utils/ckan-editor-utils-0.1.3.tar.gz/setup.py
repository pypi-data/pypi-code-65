# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ckan_editor_utils']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.15.16,<2.0.0', 'requests>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'ckan-editor-utils',
    'version': '0.1.3',
    'description': 'Utilities for editing CKAN using its API.',
    'long_description': '## Introduction\nThis library assists CKAN editors with doing batch edits and pairs well with a library like pandas.\n\n## Example usage\n\n### Simple API commands\n\n### Managed API commands\n```python\nwith ckan_editor_utils.CKANEditorSession(ckan_url, ckan_key) as ckaneu:\n    return ckaneu.delete_dataset(dataset_id).result\n```\n',
    'author': 'Eric McCowan',
    'author_email': 'eric.mccowan@servian.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
