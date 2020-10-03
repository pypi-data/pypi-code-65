# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['snowday',
 'snowday.acl',
 'snowday.acl.grants',
 'snowday.connector',
 'snowday.context',
 'snowday.graph',
 'snowday.objects',
 'snowday.types',
 'snowday.types.compression',
 'snowday.types.data',
 'snowday.types.encoding',
 'snowday.types.format',
 'snowday.types.functions',
 'snowday.types.parameters',
 'snowday.util']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.14.24,<2.0.0',
 'loguru>=0.5.1,<0.6.0',
 'networkx==2.4',
 'snowflake-connector-python==2.2.9']

setup_kwargs = {
    'name': 'snowday',
    'version': '0.1.5',
    'description': 'Tools for turning Snowflake into a Snow Day. ❄️',
    'long_description': '![Snowday](readme_src/snowday-light.png)\n\n\nTools for turning [Snowflake](https://www.snowflake.com/) into a Snow Day. ❄️\n\nA little bit of sass with a whole lot of `@dataclass`.\n\n\n\n### Installation\n\n\n```\npip install snowday\n```\n\n\n### What does it do?\n\n#### Connector\n\n![Snowday Connector 1](readme_src/conn1.gif)\n\n![Snowday Connector 2](readme_src/conn2.gif)\n\n\n#### Objects\n\n![Snowday Objects 1](readme_src/obj1.gif)\n\n![Snowday Objects 2](readme_src/obj2.gif)\n\n\n#### All together now\n\n![Snowday All Together](readme_src/alltogether.gif)\n\n\n### License\n\n\nSnowday is licensed under GPLv3.0.\n',
    'author': 'Jake Thomas',
    'author_email': 'j@silverton.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/silverton-io/snowday',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
