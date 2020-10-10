# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['randen']

package_data = \
{'': ['*']}

install_requires = \
['Sphinx>=3.2.1,<4.0.0',
 'numpy>=1.19.2,<2.0.0',
 'pandas>=1.1.2,<2.0.0',
 'pylint>=2.6.0,<3.0.0',
 'pytest>=6.1.1,<7.0.0',
 'sphinx-rtd-theme>=0.5.0,<0.6.0',
 'tox>=3.20.0,<4.0.0']

setup_kwargs = {
    'name': 'randen',
    'version': '1.0.0',
    'description': 'Random dataframe generator',
    'long_description': "Randen: Random DataFrame Generator\n==================================\n.. image:: https://raw.githubusercontent.com/varskann/randen/main/docs/source/_static/randen.PNG\n\n\n**Randen** is a minimal utility module for generating Pandas dataframes\nIt exposes a handful of methods to quickly generate big random dataframes.\n\n\nHow to Install\n--------------\n\nRanden can be installed as like any other python module, via pip\n\n::\n\n    pip install randen\n\n\nBasic Usage\n-----------\nWithin the python script::\n\n    from randen import DataFrameGenerator\n    dfg = DataFrameGenerator()\n    data_frame = dfg.get_dataframe(...)\n\n\nMotivation\n----------\nRecently, while benchmarking Pandas binary file format I/O for a project, I needed to\ngenerate multiple big dataframes. Hence, publishing this utility as a package to reduce redundant ad-hoc work\n\nIf you need some enhancements in the package, feel free to raise a Pull request or drop\na note to varskann993@gmail.com\n\nIf this isn't what you need at all,\nenjoy a trip to the original `Randen <https://en.wikipedia.org/wiki/Randen_(mountain_range)>`_.\n",
    'author': 'Kanishk Varshney',
    'author_email': 'varskann1993@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/varskann/randen',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
