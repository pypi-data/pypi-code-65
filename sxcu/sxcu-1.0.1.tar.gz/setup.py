# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sxcu']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'sxcu',
    'version': '1.0.1',
    'description': 'Python API wraper for sxcu.net',
    'long_description': '# SXCU Python API Wrapper\n\n<p align="center">\n  <a href="https://pypi.org/project/sxcu/">\n    <img src="https://img.shields.io/pypi/v/sxcu" alt="sxcu PyPI Version">\n  </a>\n  <a href="https://sxcu.syrusdark.website">\n    <img src="https://readthedocs.org/projects/sxcu/badge/?version=latest" alt="sxcu Documentation Status">\n  </a>\n  <a href="https://opensource.org/licenses/Apache-2.0">\n    <img src="https://img.shields.io/badge/License-Apache2.0-green.svg" alt"sxcu License">\n  </a>\n  <a href="https://codecov.io/gh/naveen521kk/sxcu">\n    <img src="https://codecov.io/gh/naveen521kk/sxcu/branch/master/graph/badge.svg" alt="sxcu codecov">\n  </a>\n</p>\n\n![sxcu-logo](https://github.com/naveen521kk/sxcu/raw/master/logo/readme-logo.png)\n<p align="center">\nA friendly API wrapper around https://sxcu.net.\n</p>\n\n## Installation\n\nThe package is published on\n[PyPI](https://pypi.org/project/sxcu/) and can be installed by running:\n```sh\npip install sxcu\n```\n\n## Basic Use\n\nEasily query the sxcu.net from you Python code. The data returned from the sxcu.net\nAPI is mapped to python resources:\n\n```python\n>>> import sxcu\n>>> con = sxcu.SXCU()\n>>> con.upload_image("foo.jpg")\n{\'url\': \'https://sxcu.net/2kW7IT\', \'del_url\': \'https://sxcu.net/d/2kW7IT/455c7e40-9e3b-43fa-a95a-ac17dd920e55\', \'thumb\': \'https://sxcu.net/t/2kW7IT.jpeg\'}\n```\nReady for more? Look at our whole [documentation](https://sxcu.syrusdark.website/) on Read The Docs.\n\n## Contributing\nPlease refer to [CONTRIBUTING.md](CONTRIBUTING.md) file for more information on how to\ncontribute to this project.\n',
    'author': 'Naveen M K',
    'author_email': 'naveen@syrusdark.website',
    'maintainer': 'Naveen M K',
    'maintainer_email': 'naveen@syrusdark.website',
    'url': 'https://github.com/naveen521kk/sxcu',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
