# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tracktoberfest']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'colorama>=0.4.3,<0.5.0',
 'httpx>=0.15.5,<0.16.0',
 'iso8601>=0.1.13,<0.2.0']

entry_points = \
{'console_scripts': ['tracktoberfest = tracktoberfest.main:main']}

setup_kwargs = {
    'name': 'tracktoberfest',
    'version': '0.1.0',
    'description': 'Hacktoberfest participation tracker',
    'long_description': '# tracktoberfest\n\nRetrieve Hacktoberfest contributions for a list of GitHub usernames.\n\nTheir "validity" is calculated based on the rules enumerated in the Digital\nOcean blog post: <https://hacktoberfest.digitalocean.com/hacktoberfest-update>\n\nExample:\n\n```console\n> tracktoberfest tarkatronic\nRetrieving contributions for tarkatronic...\ntarkatronic\n    Counted! - https://github.com/godaddy/tartufo/pull/111\n    Counted! - https://github.com/godaddy/tartufo/pull/109\n    Counted! - https://github.com/godaddy/tartufo/pull/103\n```\n\n## Installation\n\n```console\n> pip install tracktoberfest\n```\n',
    'author': 'Joey Wilhelm',
    'author_email': 'tarkatronic@gmail.com',
    'maintainer': 'Joey Wilhelm',
    'maintainer_email': 'tarkatronic@gmail.com',
    'url': 'https://github.com/godaddy/tracktoberfest/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
