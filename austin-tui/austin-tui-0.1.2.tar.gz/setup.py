# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['austin_tui',
 'austin_tui.controllers',
 'austin_tui.models',
 'austin_tui.view',
 'austin_tui.widgets']

package_data = \
{'': ['*']}

install_requires = \
['austin-python>=0.1.0,<0.2.0',
 'importlib-resources>=2.0.1,<3.0.0',
 'lxml>=4.5.1,<5.0.0']

extras_require = \
{':sys_platform == "win32"': ['windows-curses>=2.1.0,<3.0.0']}

entry_points = \
{'console_scripts': ['austin-tui = austin_tui.__main__:main']}

setup_kwargs = {
    'name': 'austin-tui',
    'version': '0.1.2',
    'description': 'The top-like text-based user interface for Austin',
    'long_description': '<p align="center">\n  <br><img src="art/logo.png" alt="Austin TUI" /><br>\n</p>\n\n<h3 align="center">A Top-like Interface for Austin</h3>\n\n<p align="center">\n  <img src="https://upload.wikimedia.org/wikipedia/commons/3/3a/Tux_Mono.svg"\n       height="24px" />\n  &nbsp;&nbsp;&nbsp;&nbsp;\n  <img src="https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg"\n       height="24px" />\n  &nbsp;&nbsp;&nbsp;&nbsp;\n  <img src="https://upload.wikimedia.org/wikipedia/commons/2/2b/Windows_logo_2012-Black.svg"\n       height="24px" />\n</p>\n\n<p align="center">\n  <a href="https://github.com/P403n1x87/austin-tui/actions?workflow=Tests">\n    <img src="https://github.com/P403n1x87/austin-tui/workflows/Tests/badge.svg"\n         alt="GitHub Actions: Tests">\n  </a>\n  <a href="https://travis-ci.com/P403n1x87/austin-tui">\n    <img src="https://travis-ci.com/P403n1x87/austin-tui.svg?token=fzW2yzQyjwys4tWf9anS"\n         alt="Travis CI">\n  </a>\n  <!-- <a href="https://codecov.io/gh/P403n1x87/austin-tui">\n    <img src="https://codecov.io/gh/P403n1x87/austin-tui/branch/master/graph/badge.svg"\n         alt="Codecov">\n  </a> -->\n  <a href="https://pypi.org/project/austin-tui/">\n    <img src="https://img.shields.io/pypi/v/austin-tui.svg"\n         alt="PyPI">\n  </a>\n  <a href="https://github.com/P403n1x87/austin-tui/blob/master/LICENSE.md">\n    <img src="https://img.shields.io/badge/license-GPLv3-ff69b4.svg"\n         alt="LICENSE">\n  </a>\n</p>\n\n<p align="center">\n  <a href="#synopsis"><b>Synopsis</b></a>&nbsp;&bull;\n  <a href="#installation"><b>Installation</b></a>&nbsp;&bull;\n  <a href="#usage"><b>Usage</b></a>&nbsp;&bull;\n  <a href="#compatibility"><b>Compatibility</b></a>&nbsp;&bull;\n  <a href="#contribute"><b>Contribute</b></a>\n</p>\n\n<p align="center">\n  <a\n    href="https://www.buymeacoffee.com/Q9C1Hnm28"\n    target="_blank">\n  <img\n    src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png"\n    alt="Buy Me A Coffee" />\n  </a>\n</p>\n\n# Synopsis\n\nThe Python TUI is a top-like text-based user interface for Austin, written in\npure Python. Originally planned as a sample application to showcase Austin uses,\nit\'s been promoted to a full-fledged project thanks to great popularity.\n\n<p align="center">\n  <img src="art/austin-tui.gif"\n       style="box-shadow: #111 0px 0px 16px;"\n       alt="Austin TUI" />\n</p>\n\nThe header shows you the information of the application that is being profiled,\nlike its PID, the command line used to invoke it, as well as a plot of the\namount of CPU and memory that is being used by it, in a system-monitor style.\n\n# Installation\n\nAustin TUI can be installed directly from PyPI with\n\n~~~ bash\npip install austin-tui --upgrade\n~~~\n\n**NOTE** In order for the TUI to work, the Austin 2 binary needs to be on the\n``PATH`` environment variable. See [Austin\ninstallation](https://github.com/P403n1x87/austin#installation) instructions to\nsee how you can easily install Austin on your platform.\n\n# Usage\n\nOnce Austin and Austin TUI are installed, you can start using them\nstraight-away. If you want to launch and profile a Python script, say\n`myscript.py`, you can do\n\n~~~ bash\naustin-tui python3 myscript.py\n~~~\n\nor, if `myscript.py` is an executable script,\n\n~~~ bash\naustin-tui myscript.py\n~~~\n\nLike Austin, the TUI can also attach to a running Python application. To analyse\nthe frame stacks of all the processes of a running WSGI server, for example, get\nhold of the PID of the parent process and do\n\n~~~ bash\nsudo austin-tui -Cp <pid>\n~~~\n\nThe `-C` option will instruct Austin to look for child Python processes, and you\nwill be able to navigate through them with the arrow keys.\n\n> The TUI is based on `python-curses`. The version included with the standard\n> Windows installations of Python is broken so it won\'t work out of the box. A\n> solution is to install the the wheel of the port to Windows from\n> [this](https://www.lfd.uci.edu/~gohlke/pythonlibs/#curses) page. Wheel files\n> can be installed directly with `pip`, as described in the\n> [linked](https://pip.pypa.io/en/latest/user_guide/#installing-from-wheels)\n> page.\n\n## Full mode\n\nBy default, Austin TUI shows you statistics of the last seen stack for each\nprocess and thread when the UI is refreshed (about every second). This is\nsimilar to what top does with all the running processes on your system.\n\n<p align="center">\n  <img src="art/austin-tui-normal-mode.png"\n       style="box-shadow: #111 0px 0px 16px;"\n       alt="Austin TUI - Default mode" />\n</p>\n\nIf you want to see all the collected statistics, with the frame stacks\nrepresented as a rooted tree, you can press `F` to enter the _Full_ mode. The\nlast seen stack will be highlighted so that you also have that information\navailable while in this mode.\n\n<p align="center">\n  <img src="art/austin-tui-full-mode.png"\n       style="box-shadow: #111 0px 0px 16px;"\n       alt="Austin TUI - Full mode" />\n</p>\n\n## Save statistics\n\nPeeking at a running Python application is nice but in many cases you would want\nto save the collected data for further offline analysis (for example, you might\nwant to represent it as a flame graph). At any point, whenever you want to dump\nthe collected data to a file, you can press the `S` key and a file with all the\nsamples will be generated for you in the working directory, prefixed with\n`austin_` and followed by a timestamp. The TUI will notify of the successful\noperation on the bottom-right corner.\n\n<p align="center">\n  <img src="art/austin-tui-save.png"\n       style="box-shadow: #111 0px 0px 16px;"\n       alt="Austin TUI - Save notification" />\n</p>\n\n# Compatibility\n\nAustin TUI has been tested with Python 3.6-3.9 and is known to work on\n**Linux**, **MacOS** and **Windows**.\n\nSince Austin TUI uses Austin to collect samples, the same note applies here:\n\n> Due to the **System Integrity Protection** introduced in **MacOS** with El\n> Capitan, Austin cannot profile Python processes that use an executable located\n> in the `/bin` folder, even with `sudo`. Hence, either run the interpreter from\n> a virtual environment or use a Python interpreter that is installed in, e.g.,\n> `/Applications` or via `brew` with the default prefix (`/usr/local`). Even in\n> these cases, though, the use of `sudo` is required.\n\n\n# Contribute\n\nIf you like Austin TUI and you find it useful, there are ways for you to\ncontribute.\n\nIf you want to help with the development, then have a look at the open issues\nand have a look at the [contributing guidelines](CONTRIBUTING.md) before you\nopen a pull request.\n\nYou can also contribute to the development of the Austin TUI by becoming a\nsponsor and/or by [buying me a coffee](https://www.buymeacoffee.com/Q9C1Hnm28)\non BMC or by chipping in a few pennies on\n[PayPal.Me](https://www.paypal.me/gtornetta/1).\n\n<p align="center">\n  <a href="https://www.buymeacoffee.com/Q9C1Hnm28"\n     target="_blank">\n  <img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png"\n       alt="Buy Me A Coffee" />\n  </a>\n</p>\n',
    'author': 'Gabriele N. Tornetta',
    'author_email': 'phoenix1987@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/P403n1x87/austin-tui',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
