# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['requests_whaor']

package_data = \
{'': ['*'], 'requests_whaor': ['templates/*']}

install_requires = \
['docker>=4.3.1,<5.0.0',
 'enlighten>=1.6.2,<2.0.0',
 'jinja2>=2.11.2,<3.0.0',
 'loguru>=0.5.2,<0.6.0',
 'more_itertools>=8.5.0,<9.0.0',
 'pydantic>=1.6.1,<2.0.0',
 'python-decouple>=3.3,<4.0',
 'requests[socks]>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'requests-whaor',
    'version': '0.2.1',
    'description': 'Requests With High Availability Onion Router. For the filthiest web scrapers that have no time for rate-limits.',
    'long_description': "# **requests-whaor** [[ri-kwests](https://www.dictionary.com/browse/requests) [hawr](https://www.dictionary.com/browse/whore)]\n\n[**Requests**](https://requests.readthedocs.io) **+** [**Docker**](https://www.docker.com/) **+** [**HAproxy**](http://www.haproxy.org/) **+** [**Tor**](https://www.torproject.org/)\n\n**Requests** **W**ith **H**igh **A**vailability **O**nion **R**outer. For the filthiest web scrapers that have no time for rate-limits.\n\n[![Black](https://img.shields.io/badge/code%20style-black-black?style=for-the-badge&logo=appveyor)](https://github.com/psf/black)\n[![GitHub](https://img.shields.io/github/license/dgnsrekt/requests-whaor?style=for-the-badge)](https://raw.githubusercontent.com/dgnsrekt/requests-whaor/master/LICENSE)\n\n\n## Overview\n**requests-whaor** proxies GET requests through a local **Docker** network of **TOR** circuits. It takes care of starting and stopping a pool of **TOR** proxies behind an **HAproxy** load balancer, which acts as a round robin reverse proxy network. This will give each request a new IP address.  If you start having issues with the initial pool of IPs, **requests-whaor** can gather a new pool of IP addresses by restarting all **TOR** containers.\n\n## Install with pip\n```\npip install requests-whaor\n```\n\n## Install with [Poetry](https://python-poetry.org/)\n```\npoetry add requests-whaor\n```\n\n\n## [>> **Quickstart** / **Docs** <<](https://dgnsrekt.github.io/requests-whaor/quickstart)\n\n## Projects to highlight.\n* [**dperson's**](https://hub.docker.com/u/dperson) - [torproxy docker container](https://hub.docker.com/r/dperson/torproxy)\n* [**zet4's**](https://github.com/zet4) - [alpine-tor library](https://github.com/zet4/alpine-tor)\n* [torproject](https://www.torproject.org/)\n* [haproxy](https://hub.docker.com/_/haproxy)\n\n## Useful Docker commands.\n### If things get out of hand you may need these commands for debugging or killing containers.\n```\ndocker ps -q --filter ancestor=osminogin/tor-simple | xargs -L 1 docker logs --follow\n\ndocker ps -q --filter ancestor=osminogin/haproxy | xargs -L 1 docker logs --follow\n\ndocker stop $(docker ps -q --filter ancestor=osminogin/tor-simple)\n\ndocker stop $(docker ps -q --filter ancestor=haproxy)\n\ndocker network rm $(docker network ls -q -f name=whaornet)\n```\n\n## TODO\n* [ ] Testing.\n* [ ] More request methods if requested.\n* [ ] Options for using different Tor containers.\n* [ ] Options for different load balancer containers.\n\n## Contact Information\nTelegram = Twitter = Tradingview = Discord = @dgnsrekt\n\nEmail = dgnsrekt@pm.me\n",
    'author': 'dgnsrekt',
    'author_email': 'dgnsrekt@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://dgnsrekt.github.io/requests-whaor/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
