# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lambda_extension_framework']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'lef',
    'version': '0.1.2',
    'description': 'Framework for creating AWS Lambda Extensions',
    'long_description': '# Python Extension Framework\n\nThis is a framework for building [AWS Lambda Extensions](https://aws.amazon.com/blogs/compute/introducing-aws-lambda-extensions-in-preview/).\n\n## Quickstart\n\n```bash\n$ pip install lef\n```\n\nTo get started you can use the default `Extension` class, or extend it.\n\nExample:\n\n```python\nimport lef\n\ndef handler(event):\n    print(event)\n\nextension = lef.Extension()\nextension.register([lef.EventType.INVOKE], handler)\n```\n\n## Development\n\nInstall Dependencies\n\n```bash\n$ poetry install --dev\n```\n\nBump Version\n\nYou can use the `bin/bump` script to bump the version. This is a wrapper for [bumpversion](https://pypi.org/project/bumpversion/).\n\n```bash\n$ bin/bump <VERSION LEVEL>\n```\n',
    'author': 'Joe Snell',
    'author_email': 'joepsnell@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lambda-extensions/python-extension-framework',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
