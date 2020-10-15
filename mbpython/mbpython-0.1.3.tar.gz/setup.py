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
    'version': '0.1.3',
    'description': 'Miniblink binding for python',
    'long_description': '# MBPython\n\nMiniblink is a lighter browser widget base on chromium,\njust one file, faster browser kernel of blink to integrate HTML UI in your app.\n\nMBPython is an open source project founded by lochen to provide python bindings for the Miniblink. Examples of embedding Miniblink browser are available for many popular GUI toolkits including: wxPython, PyQt, PySide, Kivy, Panda3D, PyGTK, PyGObject, PyGame/PyOpenGL and PyWin32.\n\nBy using C interface, you can create a browser just some line code.\nThere are many use cases for MBPython. You can embed a web browser control based on MBPython with great HTML 5 support. You can use it to create a HTML 5 based GUI in an application, this can act as a replacement for standard GUI toolkits like wxWidgets, Qt or GTK. You can render web content off-screen in application that use custom drawing frameworks. You can use it for automated testing of existing applications. You can use it for web scraping or as a web crawler, or other kind of internet bots.\n\n### Latest release\n\nOS | Py3 | 32bit | 64bit | Requirements\n--- | --- | --- | --- | ---\nWindows | 3.6+ | Yes | Yes | Windows 7+\n\n### Installation\n\n```bash\npip install --user MBPython\n```\n\n### How to use\nMust create a new file named config.py like this demo → https://github.com/lochen88/MBPython/blob/master/tests/config.py\nand download the node.dll add to your project.\n\nCreate a simple Window\n```bash\nfrom MBPython import miniblink\nwke=miniblink.MiniBlink\nmb=wke.init()\nwindow=wke.window\nwebview=window.wkeCreateWebWindow(0,0,0,860,760)\nwindow.wkeShowWindow(webview)\nwindow.wkeRunMessageLoop()\n```\n\n### PyInstaller\n\n```bash\npyinstall xxx.py --noconsole\n```\n\n### Examples\n\nSee the [tests](https://github.com/lochen88/MBPython/tree/master/tests) folder\n\n### Documents\n\nSee the [documents](https://github.com/lochen88/MBPython/tree/master/documents) folder\n\n### What about CEF?\n\nIn short: I do not like CEF, it is too big, comes with too many dependency resolution library, and I think we can make a better and more intuitive one. Here are a few things that I don\'t like.\n\n### Resources\n\n<table border="0">\n    <tr>\n        <td width="50%" valign="top">\n            <p align="center">\n                <img src="https://s1.ax1x.com/2020/10/15/0onOBV.jpg">\n            </p>\n            if you have any questions,you can contact me,and i will try my best to help you\n        </td>\n        <td width="50%" valign="top">\n            <p align="center">\n                <img src="https://s1.ax1x.com/2020/10/15/0onIhQ.jpg">\n            </p>\n            If you would like to support general MBPython development efforts by making a donation then please scan to pay by the alipay\n        </td>\n    </tr>\n</table>\n\n* [Project Website](https://github.com/lochen88/MBPython)\n* [Issue Tracker](https://github.com/lochen88/MBPython/issues)\n* [Official Website](https://weolar.github.io/miniblink/)\n* [QQ Group-198671899](https://qm.qq.com/cgi-bin/qm/qr?k=JipVq9gRdpPf4dqjPK9bkL99u-_BLwZz&jump_from=webapi)\n\n\n',
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
