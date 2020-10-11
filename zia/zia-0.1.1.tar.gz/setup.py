# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zia']

package_data = \
{'': ['*'], 'zia': ['data/config.yaml']}

install_requires = \
['PyYAML>=5.3.1,<6.0.0', 'requests>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'zia',
    'version': '0.1.1',
    'description': 'Python SDK for Zscaler Internet Access',
    'long_description': '# Zscaler Python SDK \n\nThis is a Python SDK for Zscaler Internet Access.  This client library is designed to support the Zscaler Internet Access (ZIA) [API](https://help.zscaler.com/zia/about-api) and [SD-WAN API](https://help.zscaler.com/zia/sd-wan-api-integration) (aka "Partner API").  All API referecnes can be found here [[LINK](https://help.zscaler.com/zia/api)].  **PLEASE READ THE DOCUMENTATION BEFORE CONTACTING ZSCALER**\n\nThis SDK has been developed mainly using Python 3.8.5 on Ubuntu 20.04 LTS (Focal Fossa).\n\n**NOTE:** This repository will experience frequent updates.  To minimize breakage, public method names will not change.  If you run into any defects, please open issues [[HERE.](https://github.com/omitroom13/zia/issues)]\n\n## Quick Start \n\n1) If you have not verified your credentials, we suggest starting [[HERE](https://help.zscaler.com/zia/configuring-postman-rest-api-client)], unless you are already familar with this API.\n\n2) Set profile\n \n```\n$ mkdir ~/.zscaler\n$ cat > ~/.zscaler/profile.yaml <<EOF\ndefault:\n  url: https://admin.<ZIA-CLOUD>.net\n  username: <ZIA-ADMIN-USER-ID>\n  password: <ZIA-ADMIN-USER-PASSWORD>\n  apikey: <ZIA-API-KEY>\npartner:\n  url: https://admin.<ZIA-CLOUD>.net\n  username: <ZIA-PARTNER-ADMIN-USER-ID>\n  password: <ZIA-PARTNER-ADMIN-USER-PASSWORD>\n  apikey: <PARTNER-API-KEY>\nEOF\n```\n        \n3) Clone Repository (OS must have git installed)\n\n```\n$ git clone https://github.com/omitroom13/zia.git\n$ cd zia/\n```\n\n4) Install SDK requirements (OS must have python3 installed)\n\n```\n$ pip install -r requirements.txt\n```\n\n5) Install SDK\n\n```\n$ python setup.py install\n```\n\n6) Check out examples\n\n```\n$ ls examples/\n...\n```\n\n## API Support\n\n### SD-WAN (Partner) API\n\n* **VPN Credentials**\n* **Locations**\n* **Activate**\n\n## Licensing\n\nThis work is released under the MIT license, forked from [eparra\'s zscaler-python-sdk v0.5](https://github.com/eparra/zscaler-python-sdk/). A copy of the license is provided in the [LICENSE](https://github.com/omitroom13/zia/blob/master/LICENSE) file.\n\n## Reporting Issues\n\nIf you have bugs or other issues specifically pertaining to this library, file them [here](https://github.com/omitroom13/zia/issues).\n\n## References\n\n* https://help.zscaler.com/zia/api\n* https://help.zscaler.com/zia/zscaler-api-developer-guide\n* https://help.zscaler.com/zia/sd-wan-api-integration\n',
    'author': 'omitroom13',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/omitroom13',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
