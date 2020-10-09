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
    'version': '0.1.0',
    'description': 'Framework for creating AWS Lambda Extensions',
    'long_description': '# Python Extension Framework\n\nThis is a framework for building [AWS Lambda Extensions](https://aws.amazon.com/blogs/compute/introducing-aws-lambda-extensions-in-preview/).\n\n## Quickstart\n\n```bash\n$ pip install lef\n```\n\nTo get started you can use the default `Extension` class, or extend it.\n\nExample:\n\n```python\nfrom lef import Extension\n\ndef handler(event):\n    print(event)\n\nextension = Extension()\nextension.register([EventType.INVOKE], handler)\n```\n',
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
