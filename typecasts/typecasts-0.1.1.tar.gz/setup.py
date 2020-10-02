# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['typecasts']

package_data = \
{'': ['*']}

install_requires = \
['documented>=0.1.1,<0.2.0']

extras_require = \
{':python_version < "3.8"': ['backports.cached-property>=1.0.0,<2.0.0'],
 ':python_version >= "3.6.0" and python_version < "3.7.0"': ['dataclasses==0.7']}

setup_kwargs = {
    'name': 'typecasts',
    'version': '0.1.1',
    'description': 'Implicit type conversions for Python',
    'long_description': "# typecasts\n\n[![Build Status](https://travis-ci.com/python-platonic/typecasts.svg?branch=master)](https://travis-ci.com/python-platonic/typecasts)\n[![Coverage](https://coveralls.io/repos/github/python-platonic/typecasts/badge.svg?branch=master)](https://coveralls.io/github/python-platonic/typecasts?branch=master)\n[![Python Version](https://img.shields.io/pypi/pyversions/typecasts.svg)](https://pypi.org/project/typecasts/)\n[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n![PyPI - License](https://img.shields.io/pypi/l/typecasts)\n\nConvert from one Python type to another in a centralized way.\n\n\n## Features\n\n```python\nfrom typecasts import casts\n\nstr_to_bytes_coder = casts[str, bytes]\n\nstr_to_bytes_coder('boo')\n# b'boo'\n```\n\n## Installation\n\n```bash\npip install typecasts\n```\n\n\n## Credits\n\nThis project was generated with [`wemake-python-package`](https://github.com/wemake-services/wemake-python-package). Current template version is: [cf0afc42e6f5f3886be1d93b6c56b0f422b3a15a](https://github.com/wemake-services/wemake-python-package/tree/cf0afc42e6f5f3886be1d93b6c56b0f422b3a15a). See what is [updated](https://github.com/wemake-services/wemake-python-package/compare/cf0afc42e6f5f3886be1d93b6c56b0f422b3a15a...master) since then.\n",
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/python-platonic/typecasts',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
