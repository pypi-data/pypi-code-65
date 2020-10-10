# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['austin_web', 'austin_web.html']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.6.2,<4.0.0',
 'austin-python>=0.1.0,<0.2.0',
 'halo>=0.0.29,<0.0.30',
 'importlib_resources>=3.0.0,<4.0.0',
 'pyfiglet>=0.8.post1,<0.9']

entry_points = \
{'console_scripts': ['austin-web = austin_web.__main__:main']}

setup_kwargs = {
    'name': 'austin-web',
    'version': '0.1.0',
    'description': 'Flame graph web application for Austin',
    'long_description': '<p align="center">\n  <br>\n  <img width="320px" src="art/logo.png" alt="Austin Web">\n  <br>\n</p>\n\n<h3 align="center">A Modern Web Interface for Austin</h3>\n\n<p align="center">\n  <img src="https://upload.wikimedia.org/wikipedia/commons/3/3a/Tux_Mono.svg"\n       height="24px" />\n  &nbsp;&nbsp;&nbsp;&nbsp;\n  <img src="https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg"\n       height="24px" />\n  &nbsp;&nbsp;&nbsp;&nbsp;\n  <img src="https://upload.wikimedia.org/wikipedia/commons/2/2b/Windows_logo_2012-Black.svg"\n       height="24px" />\n</p>\n\n<p align="center">\n  <a href="https://github.com/P403n1x87/austin-web/actions?workflow=Tests">\n    <img src="https://github.com/P403n1x87/austin-web/workflows/Tests/badge.svg"\n         alt="GitHub Actions: Tests">\n  </a>\n  <a href="https://travis-ci.com/P403n1x87/austin-web">\n    <img src="https://travis-ci.com/P403n1x87/austin-web.svg?token=fzW2yzQyjwys4tWf9anS"\n         alt="Travis CI">\n  </a>\n  <a href="https://codecov.io/gh/P403n1x87/austin-web">\n    <img src="https://codecov.io/gh/P403n1x87/austin-web/branch/master/graph/badge.svg"\n         alt="Codecov">\n  </a>\n  <a href="https://pypi.org/project/austin-web/">\n    <img src="https://img.shields.io/pypi/v/austin-web.svg"\n         alt="PyPI">\n  </a>\n  <a href="https://github.com/P403n1x87/austin-web/blob/master/LICENSE.md">\n    <img src="https://img.shields.io/badge/license-GPLv3-ff69b4.svg"\n         alt="LICENSE">\n  </a>\n</p>\n\n<p align="center">\n  <a href="#synopsis"><b>Synopsis</b></a>&nbsp;&bull;\n  <a href="#installation"><b>Installation</b></a>&nbsp;&bull;\n  <a href="#usage"><b>Usage</b></a>&nbsp;&bull;\n  <a href="#compatibility"><b>Compatibility</b></a>&nbsp;&bull;\n  <a href="#contribute"><b>Contribute</b></a>\n</p>\n\n<p align="center">\n  <a href="https://www.buymeacoffee.com/Q9C1Hnm28"\n     target="_blank">\n  <img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png"\n       alt="Buy Me A Coffee" />\n  </a>\n</p>\n\n# Synopsis\n\nAustin Web is a modern web interface for Austin, based on\n[D3.js](https://d3js.org/) and [tailwindcss](https://tailwindcss.com/). It is\nyet another example of how to use Austin to make a visual profiling tool for\nPython. The flame graph is generated using\n[d3-flame-graph](https://github.com/spiermar/d3-flame-graph).\n\n<p align="center">\n  <img src="art/austin-web-serve.gif"\n       style="box-shadow: #111 0px 0px 16px;" />\n</p>\n\nAustin Web offers two main functionalities. The default one is to serve a web\npage that allows you to have a live view of the metrics collected by Austin. The\nvisualisation is a _live_ flame graph in your browser that refreshes every 3\nseconds with newly collected data. Hence, Austin Web can also be used for\n_remote_ profiling.\n\nYou can also run Austin Web in _compile_ mode to generate a static flame graph\nHTML page, much like\n[flamegraph.pl](https://github.com/brendangregg/FlameGraph), but with the full\nAustin Web UI around it.\n\n\n# Installation\n\nAustin Web can be installed from PyPI simply with\n\n~~~ bash\npip install austin-web\n~~~\n\n> **NOTE** Austin Web relies on the\n> [Austin](https://github.com/P403n1x87/austin) binary being available from the\n> `PATH` environment variable. So make sure that Austin is properly installed on\n> your system. See\n> [Austin installation](https://github.com/P403n1x87/austin#installation)\n> instruction for more details on how to get Austin installed on your platform.\n\n\n# Usage\n\nYou can run Austin Web simply with\n\n~~~ bash\naustin-web python3 myscript.py\n~~~\n\nto start serving on localhost over an ephemeral port. If `myscript.py` is an\nexecutable script, you can simply do\n\n~~~ bash\naustin-web myscript.py\n~~~\n\nIf you want to specify the host and the port, you can pass the `--host` and\n`--port` options to the command line. For example, to serve for the World on\nport 5050, use\n\n~~~ bash\naustin-web --host 0.0.0.0 --port 5050 python3 myscript.py\n~~~\n\nIf you want to compile the collected metrics into a static HTML page, you can\nrun Austin Web in compile mode by passing the `--compile` option, followed by\nthe destination file name, e.g.\n\n~~~ bash\naustin-web --compile output.html python3 myscript.py\n~~~\n\nLike Austin, you can use Austin Web to profile any running Python application.\nFor example, to profile a WSGI server and all its child processes, get hold of\nits PID and do\n\n~~~ bash\nsudo austin-web -Cp <pid>\n~~~\n\n\n# Compatibility\n\nAustin Web has been tested with Python 3.6-3.9 and is known to work on\n**Linux**, **MacOS** and **Windows**.\n\nAustin Web is known to have some minor issues on Windows. When started in serve\nmode, pressing `Ctrl+C` might not actually stop Austin Web.\n\nSince Austin Web uses Austin to collect samples, the same note applies here:\n\n> Due to the **System Integrity Protection** introduced in **MacOS** with El\n> Capitan, Austin cannot profile Python processes that use an executable located\n> in the `/bin` folder, even with `sudo`. Hence, either run the interpreter from\n> a virtual environment or use a Python interpreter that is installed in, e.g.,\n> `/Applications` or via `brew` with the default prefix (`/usr/local`). Even in\n> these cases, though, the use of `sudo` is required.\n\n\n# Contribute\n\nIf you want to help with the development, then have a look at the open issues\nand have a look at the [contributing guidelines](CONTRIBUTING.md) before you\nopen a pull request.\n\nYou can also contribute to the development of the Austin Web by becoming a\nsponsor and/or by [buying me a coffee](https://www.buymeacoffee.com/Q9C1Hnm28)\non BMC or by chipping in a few pennies on\n[PayPal.Me](https://www.paypal.me/gtornetta/1).\n\n<p align="center">\n  <a href="https://www.buymeacoffee.com/Q9C1Hnm28"\n     target="_blank">\n  <img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png"\n       alt="Buy Me A Coffee" />\n  </a>\n</p>\n',
    'author': 'Gabriele N. Tornetta',
    'author_email': 'phoenix1987@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/P403n1x87/austin-web',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
