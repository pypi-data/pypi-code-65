# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['data_linter']

package_data = \
{'': ['*'], 'data_linter': ['schemas/*']}

install_requires = \
['boto3>=1.14.7,<2.0.0',
 'dataengineeringutils3>=1.0.1,<2.0.0',
 'goodtables>=2.5.0,<3.0.0',
 'iam_builder>=3.7.0,<4.0.0',
 'importlib-metadata>=1.7,<2.0',
 'jsonschema>=3.2.0,<4.0.0',
 'pyyaml>=5.3.1,<6.0.0']

entry_points = \
{'console_scripts': ['data_linter = data_linter.command_line:main']}

setup_kwargs = {
    'name': 'data-linter',
    'version': '1.1.4',
    'description': 'data linter',
    'long_description': '# Data Linter\n\nA python package to to allow automatic validation of data as part of a Data Engineering pipeline. It is designed to automate the process of moving data from Land to Raw-History as described in the [ETL pipline guide](https://github.com/moj-analytical-services/etl-pipeline-example)\n\nThe validation is based on the `goodtables` package, from the fine folk at Frictionless Data. More information can be found at [their website.](https://frictionlessdata.io/tooling/goodtables/#check-it-out)\n\n## Installation\n\n```bash\npip install data_linter\n```\n\n## Usage\n\nThis package takes a `yaml` based config file written by the user (see example below), and validates data in the specified Land bucket against specified metadata. If the data conforms to the metadata, it is moved to the specified Raw bucket for the next step in the pipeline. Any failed checks are passed to a separate bucket for testing. The package also generates logs to allow you to explore issues in more detail.\n\nTo run the validation, at most simple you can use the following:\n\n```python\nfrom data_linter import run_validation\n\nconfig_path = "config.yaml"\n\nrun_validation(config_path)\n```\n\n## Example config file\n\n```yaml\nland-base-path: s3://land-bucket/my-folder/  # Where to get the data from\nfail-base-path: s3://fail-bucket/my-folder/  # Where to write the data if failed\npass-base-path: s3://pass-bucket/my-folder/  # Where to write the data if passed\nlog-base-path: s3://log-bucket/my-folder/  # Where to write logs\ncompress-data: true  # Compress data when moving elsewhere\nremove-tables-on-pass: true  # Delete the tables in land if validation passes\nall-must-pass: true  # Only move data if all tables have passed\nfail-unknown-files:\n    exceptions:\n        - additional_file.txt\n        - another_additional_file.txt\n\n# Tables to validate\ntables:\n    table1:\n        required: true  # Does the table have to exist\n        pattern: null  # Assumes file is called table1\n        metadata: meta_data/table1.json\n        linter: goodtables\n\n    table2:\n        required: true\n        pattern: ^table2\n        metadata: meta_data/table2.json\n```\n\n## How to update\n\nWe have tests that run on the current state of the `poetry.lock` file (i.e. the current dependencies). We also run tests based on the most up to date dependencies allowed in `pyproject.toml`. This allows us to see if there will be any issues when updating dependences. These can be run locally in the `tests` folder.\n\nWhen updating this package, make sure to change the version number in `pyproject.toml` and describe the change in CHANGELOG.md.\n\nIf you have changed any dependencies in `pyproject.toml`, run `poetry update` to update `poetry.lock`.\n\nOnce you have created a release in GitHub, to publish the latest version to PyPI, run:\n\n```bash\npoetry build\npoetry publish -u <username>\n```\n\nHere, you should substitute <username> for your PyPI username. In order to publish to PyPI, you must be an owner of the project.\n\n\n## Process Diagram\n\nHow logic works\n\n![](images/data_linter_process.png)',
    'author': 'Thomas Hirsch',
    'author_email': 'thomas.hirsch@digital.justice.gov.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
