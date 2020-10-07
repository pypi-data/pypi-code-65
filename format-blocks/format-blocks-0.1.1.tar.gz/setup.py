# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['format_blocks']

package_data = \
{'': ['*']}

install_requires = \
['typing_extensions>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'format-blocks',
    'version': '0.1.1',
    'description': 'A library for building code formatters',
    'long_description': "# Format Blocks\n\nFormat Blocks is a Python library for building code formatters.\n\n## Usage\n\nFormat Blocks provides a number of 'block' objects which know how to arrange text in various ways,\nsuch as `LineBlock` which arranges elements on one line, and `StackBlock` which stacks them across\nlines, and `WrapBlock` which wraps inserts line breaks at the margin.\n\nHowever, the most import block is `ChoiceBlock`. ChoiceBlock accepts multiple formatting options,\nand allows for the solver to pick the choices which _minimize the overall formatting cost_.\n\nSee the tests for some examples!\n\n## Origins\n\nFormat Blocks is a fork of the guts of Google's R Formatter, [rfmt](https://github.com/google/rfmt).\nRfmt was structured as a formatting library with an R implementation, _almost_ entirely decoupled. To\ncreate Format Blocks, I just did some final decoupling, then polished up the code and wrote some\nextra features and tests.\n",
    'author': 'Joseph Atkins-Turkish',
    'author_email': 'spacerat3004@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
