# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['apubsub']

package_data = \
{'': ['*']}

extras_require = \
{':sys_platform == "linux"': ['uvloop>=0.14.0,<0.15.0']}

setup_kwargs = {
    'name': 'apubsub',
    'version': '0.2.5',
    'description': 'Message service implementing publisher/subscriber pattern',
    'long_description': '# APubSub\n\n[![Build Status](https://travis-ci.org/outcatcher/apubsub.svg?branch=master)](https://travis-ci.org/outcatcher/apubsub)\n[![Coverage](https://codecov.io/gh/outcatcher/apubsub/branch/master/graph/badge.svg)](https://codecov.io/gh/outcatcher/apubsub)\n[![PyPI version](https://img.shields.io/pypi/v/apubsub.svg)](https://pypi.org/project/apubsub/)\n![GitHub](https://img.shields.io/github/license/outcatcher/apubsub)\n\nSimple, single-purpose message service implementation.\n\n### Installation\n\n_Python versin 3.7+ required_\n\nJust install it with pip: `pip install apubsub`\n\n### Usage\n\n\n```python\nfrom apubsub import Service\n\nservice = Service()\n\n# Note that service is started in stand-alone process\n# so start it as early as possible to minimize resource pickling*\nservice.start()\n\nclass Klass:\n\n    def __init__(self):\n        self.sub = service.get_client()\n        await self.sub.start_consuming()  # subscriber should be started\n        \n        self.pub = service.get_client()  # if used only as publisher, it is not required\n\n    async def do_smth(self):\n        data = await self.sub.get(.1)  # fetch received data with timeout\n        if data is None:\n            print("No data received by subscriber")\n            return\n        print(data)\n    \n    async def do_smth_else(self):\n        msg = "some string data"\n        await self.pub.publish("topic", msg)\n\n    async def use_iter_get(self):\n        async for data in self.sub.get_iter():\n            print(f"Data received: {data}")\n\n```\n\n_Check out more examples in tests_\n\n',
    'author': 'Anton Kachurin',
    'author_email': 'katchuring@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/outcatcher/apubsub',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
