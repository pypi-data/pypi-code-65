# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mbpython']

package_data = \
{'': ['*']}

install_requires = \
['pywin32>=228,<229']

setup_kwargs = {
    'name': 'mbpython',
    'version': '0.1.1',
    'description': 'Miniblink binding for python',
    'long_description': '# MBPython\n\nMBPython是免费版miniblink的Python封装， 龙泉寺扫地僧开发的miniblink, 地址：\nhttps://github.com/weolar/miniblink49\n\n免费版不支持多线程调用\n\n更多信息查看miniblink全新官网：https://weolar.github.io/miniblink/\n',
    'author': 'lochen',
    'author_email': '1191826896@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lochen88/MBPython',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
