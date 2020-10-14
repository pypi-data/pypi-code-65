# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ipy_pdcache', 'ipy_pdcache.tests']

package_data = \
{'': ['*']}

install_requires = \
['ipython>=7.0,<8.0', 'pandas>=1.0.0,<2.0.0']

setup_kwargs = {
    'name': 'ipy-pdcache',
    'version': '0.0.6',
    'description': 'Automatically cache results of intensive computations in IPython.',
    'long_description': "# %%pdcache cell magic\n\n[![pypi version](https://img.shields.io/pypi/v/ipy-pdcache.svg)](https://pypi.org/project/ipy-pdcache/)\n[![license](https://img.shields.io/pypi/l/ipy-pdcache.svg)](https://pypi.org/project/ipy-pdcache/)\n\nAutomatically cache results of intensive computations in IPython.\n\nInspired by [ipycache](https://github.com/rossant/ipycache).\n\n\n## Installation\n\n```bash\n$ pip install ipy-pdcache\n```\n\n\n## Usage\n\nIn IPython:\n\n```python\nIn [1]: %load_ext ipy_pdcache\n\nIn [2]: import pandas as pd\n\nIn [3]: %%pdcache df data.csv\n   ...: df = pd.DataFrame({'A': [1,2,3], 'B': [4,5,6]})\n   ...:\n\nIn [4]: !cat data.csv\n,A,B\n0,1,4\n1,2,5\n2,3,6\n```\n\nThis will cache the dataframe and automatically load it when re-executing the cell.\n\n\n%load_ext ipy_pdcache\nimport pandas as pd\n\n%%pdcache df data.csv\nprint('hu')\ndf = pd.DataFrame({'A': [1,2,3], 'B': [4,5,6]})\nprint('ha')\n1\n\n\n\nDev:\n* https://ipython.readthedocs.io/en/stable/config/extensions/\n* https://ipython.readthedocs.io/en/stable/config/custommagics.html#defining-magics\n\nTesting:\n* https://medium.com/@davide.sarra/how-to-test-magics-in-ipython-extensions-86d99e5d6802\n* https://github.com/davidesarra/jupyter_spaces/blob/master/tests/test_magics.py\n\nMisc:\n* https://ipython.readthedocs.io/en/stable/api/generated/IPython.utils.capture.html\n",
    'author': 'kpj',
    'author_email': 'kpjkpjkpjkpjkpjkpj@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kpj/ipy_pdcache',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
