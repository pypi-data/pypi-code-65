# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['twitter_blocklist']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'progressbar2>=3.51.3,<4.0.0',
 'python-twitter>=3.5,<4.0',
 'toml>=0.10.1,<0.11.0']

entry_points = \
{'console_scripts': ['twitter_blocklist = twitter_blocklist.console:main']}

setup_kwargs = {
    'name': 'twitter-blocklist',
    'version': '0.5.2',
    'description': 'Export and import Twitter blocklists',
    'long_description': "# `twitter_blocklist`\n\nExport and import Twitter blocklists.\n\n`twitter_blocklist` provides a command-line tool to export a list of all\nthe accounts you block to a text file:\n\n    $ twitter_blocklist --export my_blocks.csv\n\nor import a list from someone else, or downloaded from <https://blocktogether.org>:\n\n    $ twitter_blocklist list_to_import.csv\n\nor block all member of a Twitter list:\n\n    $ twitter_blocklist --list <list_id>\n\nundo blocking with the --unblock flag:\n\n    $ twitter_blocklist --unblock --list <list_id>\n    $ twitter_blocklist --unblock list_to_unblock.csv\n\nThe files have a CSV extension but they are actually just text files with 1 Twitter\nuser ID per line.\n\n## Install\n\n    $ pip install twitter_blocklist\n\n## Initial setup\n\nCreate a Twitter app following the [instructions from the `python-twitter` project](https://python-twitter.readthedocs.io/en/latest/getting_started.html)\n\nCreate a text file named `twitter_keys.toml` with this format:\n\n```\nconsumer_key='xxxxxxxxxxxxxxxxxxxxxxxxx'\nconsumer_secret='xxxxxxxxxxxxxxxxxxxxxxxxx'\naccess_token_key='xxxxxxxxxxxxxxxxxxxxxxxxx'\naccess_token_secret='xxxxxxxxxxxxxxxxxxxxxxxxx'\n```\n\nMake sure you have the single quotes.\n\nFrom the same folder where you have `twitter_keys.toml`, run the tool as shown above.\n",
    'author': 'Andrea Zonca',
    'author_email': 'code@andreazonca.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zonca/twitter_blocklist',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
