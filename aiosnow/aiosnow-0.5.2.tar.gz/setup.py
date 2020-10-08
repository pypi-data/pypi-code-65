# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiosnow',
 'aiosnow.models',
 'aiosnow.models.common',
 'aiosnow.models.common.schema',
 'aiosnow.models.common.schema.fields',
 'aiosnow.models.common.schema.helpers',
 'aiosnow.models.table',
 'aiosnow.models.table.declared',
 'aiosnow.query',
 'aiosnow.query.fields',
 'aiosnow.request',
 'aiosnow.request.helpers',
 'aiosnow.request.response']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.6.2,<4.0.0', 'marshmallow>=3.6.1,<4.0.0']

setup_kwargs = {
    'name': 'aiosnow',
    'version': '0.5.2',
    'description': 'Asynchronous Python ServiceNow library',
    'long_description': '# aiosnow: Asynchronous Python ServiceNow Library\n\n[![image](https://badgen.net/pypi/v/aiosnow)](https://pypi.org/project/aiosnow)\n[![image](https://badgen.net/badge/python/3.7+?color=purple)](https://pypi.org/project/aiosnow)\n[![image](https://badgen.net/travis/rbw/aiosnow)](https://travis-ci.org/rbw/aiosnow)\n[![image](https://badgen.net/pypi/license/aiosnow)](https://raw.githubusercontent.com/rbw/aiosnow/master/LICENSE)\n[![image](https://pepy.tech/badge/snow/month)](https://pepy.tech/project/snow)\n\n**aiosnow** is a Python [asyncio](https://docs.python.org/3/library/asyncio.html) library for interacting with ServiceNow programmatically. It hopes to be:\n\n- Convenient: A good deal of work is put into making **aiosnow** flexible and easy to use.\n- Performant: Remote API calls uses non-blocking sockets tracked by an event loop, allowing large amounts of lightweight request tasks to run concurrently.\n- Modular: Core functionality is componentized into modules that are built with composability and extensibility in mind.\n\n*Example code*\n\n```python\nimport asyncio\n\nimport aiosnow\nfrom aiosnow.models.table.declared import IncidentModel as Incident\n\nasync def main():\n    client = aiosnow.Client("<instance>.service-now.com", basic_auth=("<username>", "<password>"))\n\n    async with Incident(client, table_name="incident") as inc:\n        # Fetch high-priority incidents\n        for response in await inc.get(Incident.priority <= 3, limit=5):\n            print(f"Number: {response[\'number\']}, Priority: {response[\'priority\'].value}")\n\nasyncio.run(main())\n```\n\nCheck out the [examples directory](examples) for more material.\n\n### Documentation\n\nAPI reference and more is available in the [technical documentation](https://aiosnow.readthedocs.io/en/latest).\n\n\n### Funding\n\nThe **aiosnow** code is permissively licensed, and can be incorporated into any type of application–commercial or otherwise–without costs or limitations.\nIts author believes it\'s in the commercial best-interest for users of the project to invest in its ongoing development.\n\nConsider leaving a [donation](https://paypal.vault13.org) if you like this software, it will:\n\n- Directly contribute to faster releases, more features, and higher quality software.\n- Allow more time to be invested in documentation, issue triage, and community support.\n- Safeguard the future development of **aiosnow**.\n\n### Development status\n\nBeta: Core functionality is done and API breakage unlikely to happen.\n\n\n### Contributing\n\nCheck out the [contributing guidelines](CONTRIBUTING.md) if you want to help out with code or documentation.\n\n\n### Author\n\nRobert Wikman \\<rbw@vault13.org\\>\n\n',
    'author': 'Robert Wikman',
    'author_email': 'rbw@vault13.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rbw/aiosnow',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
