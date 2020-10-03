# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sndslib']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['snds = sndslib.cli:main']}

setup_kwargs = {
    'name': 'sndslib',
    'version': '0.1.1',
    'description': 'Process and verify data from SNDS easily',
    'long_description': "# SNDS LIB\n\n[![Build Status](https://travis-ci.org/undersfx/sndslib.svg?branch=master)](https://travis-ci.org/undersfx/sndslib) [![codecov](https://codecov.io/gh/undersfx/sndslib/branch/master/graph/badge.svg)](https://codecov.io/gh/undersfx/sndslib) [![Python 3](https://pyup.io/repos/github/undersfx/sndslib/python-3-shield.svg)](https://pyup.io/repos/github/undersfx/sndslib/) [![Updates](https://pyup.io/repos/github/undersfx/sndslib/shield.svg)](https://pyup.io/repos/github/undersfx/sndslib/)\n\nProcess and verify data from Microsoft's Smart Network Data Service (SNDS) API easily.\n\nSNDSLIB is a wrapper around SNDS Automated Data Access API to facilitate fast data process and analysis.\n\n\n## What is SNDS?\n\nSmart Network Data Service (SNDS) is a platform to monitor data from IPs that send emails to Microsoft's servers. If you send more than 100 messages per day from your IPs, your can get valuable information about IP reputation, possible blocks, spam complaints and spamtraps hits.\n\n\n## Talk is cheap. Show me the code!\n\nSimple example of library use:\n\n```python\n    >>> from sndslib import sndslib\n\n    >>> r = sndslib.get_ip_status('mykey')\n    >>> blocked_ips = sndslib.list_blocked_ips(r)\n    [1.1.1.1, 2.2.2.2, 3.3.3.3]\n\n    >>> r = sndslib.get_data('mykey')\n    >>> sndslib.summarize(r)\n    {'red': 272, 'green': 710, 'yellow': 852, 'traps': 1298, 'ips': 1834, 'date': '12/31/2019'}\n\n    >>> sndslib.search_ip_status('3.3.3.3', r)\n    {'activity_end': '12/31/2019 7:00 PM',\n    'activity_start': '12/31/2019 10:00 AM',\n    'comments': '',\n    'complaint_rate': '< 0.1%',\n    'data_commands': '1894',\n    'filter_result': 'GREEN',\n    'ip_address': '3.3.3.3',\n    'message_recipients': '1894',\n    'rcpt_commands': '1895',\n    'sample_helo': '',\n    'sample_mailfrom': '',\n    'trap_message_end': '',\n    'trap_message_start': '',\n    'traphits': '0'}\n```\n\n\n## CLI\n\nThis library contains a CLI to facilitate fast operations in the terminal.\n\nSome examples:\n\nSummary of all IPs status\n```bash\nsnds -k 'your-key-here' -s\n```\n\nIndividual report of a IP\n```bash\nsnds -k 'your-key-here' -ip '1.1.1.1'\n```\n\nList all IPs blocked\n```bash\nsnds -k 'your-key-here' -l\n```\n\nList all IPs blocked with rDNS\n```bash\nsnds -k 'your-key-here' -r\n```\n\n\nMore information in the [SNDS](https://sendersupport.olc.protection.outlook.com/snds/FAQ.aspx?wa=wsignin1.0) and [SNDS Automated Data Access](https://sendersupport.olc.protection.outlook.com/snds/auto.aspx) pages.\n",
    'author': 'undersfx',
    'author_email': 'undersoft.corp@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/undersfx/sndslib',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
