# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['acamodels']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.6,<2.0']

setup_kwargs = {
    'name': 'acamodels',
    'version': '0.5.3',
    'description': 'Datamodels based on pydantic used in Python tools developed at Aarhus City Archives.',
    'long_description': '[![Aarhus Stadsarkiv](https://raw.githubusercontent.com/aarhusstadsarkiv/py-template/master/img/logo.png)](https://www.aarhusstadsarkiv.dk/)\n# datamodels [![codecov](https://codecov.io/gh/aarhusstadsarkiv/datamodels/branch/master/graph/badge.svg)](https://codecov.io/gh/aarhusstadsarkiv/datamodels) [![Tests](https://github.com/aarhusstadsarkiv/datamodels/workflows/Tests/badge.svg)](https://github.com/aarhusstadsarkiv/datamodels/actions?query=workflow%3ATests)\n\n\nDatamodels based on [pydantic](https://github.com/samuelcolvin/pydantic/) used in Python tools developed at Aarhus City Archives.\n\n#### Structure\nEach model is placed in a separate `.py` file in order to achieve maintainability and better version control. In addition, each model must be served in `__init__.py` such that it is possible to call `from acamodels import model`.\n\n#### Versioning\n- **Updating** one or more models is considered a **patch** version, e.g. `0.1.0 -> 0.1.1`\n- **Adding** new models is considered a **minor** version, e.g. `0.1.0 -> 0.2.0`\n\nMajor versions will be pushed when models have reached a yet to be determined mature stage.\n',
    'author': 'Nina Jensen',
    'author_email': 'jnik@aarhus.dk',
    'maintainer': 'Aarhus Stadsarkiv',
    'maintainer_email': 'stadsarkiv@aarhus.dk',
    'url': 'https://www.aarhusstadsarkiv.dk/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
