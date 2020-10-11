# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypopulation']

package_data = \
{'': ['*'], 'pypopulation': ['resources/*']}

setup_kwargs = {
    'name': 'pypopulation',
    'version': '2020.3',
    'description': 'Population lookup via ISO 3166 country codes',
    'long_description': '![CalVer schema](https://img.shields.io/badge/CalVer-YYYY.MINOR-blue?style=flat-square)\n![Python versions](https://img.shields.io/badge/Python-v3.6.1%2B-blue?style=flat-square)\n![Flake8 & friends](https://img.shields.io/github/workflow/status/kwzrd/pypopulation/Lint%20&%20Tests?label=Tests,%20Flake8%20%26%20friends&style=flat-square)\n![Last commit](https://img.shields.io/github/last-commit/kwzrd/pypopulation/master?label=Last%20commit&style=flat-square)\n\n# pypopulation\n\nLightweight population lookup using [ISO 3166](https://en.wikipedia.org/wiki/ISO_3166) alpha-1/2 country codes for **Python 3.6.1** and higher.\n\n```python\n>>> import pypopulation\n>>> \n>>> pypopulation.get_population("DE")  # Germany\n83132799\n```\n\nThe aim is to provide a minimalist package with no dependencies that does one thing only, as best as possible. Population figures are read from a JSON file into Python dictionaries at import time. The API then only exposes the dictionaries.\n\n**The given figures are estimates at best.** Read below for more details on the data source.\n\n## Interface\n\nThe API is formed by 3 functions:\n* `get_population_a2`: population for a 2-letter country code\n* `get_population_a3`: population for a 3-letter country code\n* `get_population`: population for either a 2-letter or a 3-letter country code\n\nAll functions return `None` if no country is found for the given country code. **Lookup is case insensitive**, i.e. `"DE"` and `"de"` give same results.\n\nLookups using country names are difficult & not currently supported, but the source JSON file does contain them. This is to make the source file more comprehensible. If all you have to work with is a country name, consider using [`pycountry`](https://pypi.org/project/pycountry/) to resolve your names to ISO 3166 codes first.\n\nIf you would like to build your own wrapper around the source JSON, you can do:\n```python\ncountries: t.List[t.Dict] = pypopulation._load_file()\n```\n\n## Installation\n\nWith `pip` from [PyPI](https://pypi.org/):\n\n```\npip install pypopulation\n```\n\n## Development\n\nI\'m using [`Poetry`](https://python-poetry.org/) to maintain development dependencies. These dependencies are only used to assure code quality. They are not necessary to use the package, and are not installed in a production environment.\n\nReplicate the development environment:\n```\npoetry install\n```\n\nRun lint, tests and produce a `.coverage` file:\n```\npoetry run flake8\npoetry run coverage run -m unittest\n```\n\nThese commands run in CI (GH Actions) on pull requests against `master`. Tests are ran on all supported Python versions. Refer to the [`Checks`](.github/workflows/checks.yml) workflow for more information. New releases trigger the [`Publish`](.github/workflows/publish.yml) workflow, which builds a distribution and pushes it to PyPI.\n\n## Data source\n\nThe population figures were sourced from [The World Bank](https://data.worldbank.org/indicator/SP.POP.TOTL) (`2020-07-01`). This dataset provides the country name, alpha-3 code, and population figures found in the resource JSON file. The data was enriched with alpha-2 country codes for each row. Rows not corresponding to political countries were removed, e.g. "Middle East & North Africa (excluding high income)". Some country names were adjusted for readability, e.g. expanded abbreviations. **No adjustments were made to the population figures**. Please refer to the linked page for a more detailed description of the dataset.\n\nThis projects aims to expose the linked data to Python code. It does not guarantee correctness of the provided figures.\n',
    'author': 'kwzrd',
    'author_email': 'kay.wzrd@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kwzrd/pypopulation',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
