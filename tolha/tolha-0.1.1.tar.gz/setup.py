# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tolha']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.5.3,<0.6.0',
 'playwright>=0.142.3,<0.143.0',
 'python-decouple>=3.3,<4.0']

setup_kwargs = {
    'name': 'tolha',
    'version': '0.1.1',
    'description': 'Unofficial Library to access your my ais data',
    'long_description': '# Tolha - โทรหา\n\n> เข้าถึงประวัติการโทรของตัวเองง่ายๆ\n\n## Get Started\n```bash\n# support python 3.8+\npip install tolha\n```\n\n```python\nfrom decouple import config\nfrom tolha.myais import get_recent_call_history\n\ncall_usage = get_recent_call_history(config("PHONE_NUMBER"), config("PASSWORD"), config("NATIONAL_ID_CARD"))\nprint(call_usage)\n```\n\n## Dev\n\n### Roadmap\n1. output as pandas DataFrame\n2. able to select other month\n3. make cli\n4. add other telco\n\n### Tools\nuse <https://chrome.google.com/webstore/detail/selectorgadget/mhjhnkcfbdhnjickkkdbjoemdmbfginb>',
    'author': 'Nutchanon Ninyawee',
    'author_email': 'nutchanon@codustry.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CircleOnCircles/tolha',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
