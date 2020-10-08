# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_test', 'nonebot_test.drivers']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.5.0,<0.6.0',
 'nonebot2>=2.0.0-alpha.1,<3.0.0',
 'python-socketio>=4.6.0,<5.0.0']

setup_kwargs = {
    'name': 'nonebot-test',
    'version': '0.1.0',
    'description': 'Test frontend for nonebot v2+',
    'long_description': '<div align=center>\n  <img src="src/assets/logo.png" width="200" height="200">\n\n# nonebot-test\n\n[![License](https://img.shields.io/github/license/nonebot/nonebot-test.svg)](LICENSE)\n[![PyPI](https://img.shields.io/pypi/v/nonebot-test.svg)](https://pypi.python.org/pypi/nonebot-test)\n![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)\n![NoneBot Version](https://img.shields.io/badge/NoneBot-2+-9cf.svg)\n[![QQ 群](https://img.shields.io/badge/qq%E7%BE%A4-768887710-orange.svg)](https://jq.qq.com/?_wv=1027&k=5OFifDh)\n[![Telegram](https://img.shields.io/badge/telegram-chat-blue.svg)](https://t.me/cqhttp)\n[![QQ 版本发布群](https://img.shields.io/badge/%E7%89%88%E6%9C%AC%E5%8F%91%E5%B8%83%E7%BE%A4-218529254-green.svg)](https://jq.qq.com/?_wv=1027&k=5Nl0zhE)\n[![Telegram 版本发布频道](https://img.shields.io/badge/%E7%89%88%E6%9C%AC%E5%8F%91%E5%B8%83%E9%A2%91%E9%81%93-join-green.svg)](https://t.me/cqhttp_release)\n\n</div>\n\n## Project setup\n\n```\nnpm install\npoetry install\n```\n\n### Compiles for development\n\n```\nnpm run build\n```\n\nthen, start your bot in the same python environment where nonebot-test installed.\n\n```\npython bot.py\n```\n',
    'author': 'yanyongyu',
    'author_email': 'yanyongyu_1@126.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://v2.nonebot.dev/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
