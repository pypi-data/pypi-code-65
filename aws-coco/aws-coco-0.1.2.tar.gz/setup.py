# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aws_coco', 'aws_coco.lib']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.15.10,<2.0.0', 'requests>=2.24.0,<3.0.0']

entry_points = \
{'console_scripts': ['coco = aws_coco.main:run']}

setup_kwargs = {
    'name': 'aws-coco',
    'version': '0.1.2',
    'description': 'A utility for managing AWS Console Sessions with Firefox Containers',
    'long_description': "# AWS coco (console container)\n\nThis tool allows you to manage AWS Console Sessions with Firefox Containers\n\n## Quickstart\n\nEnsure you've  met the [requirements](#requirements).\n\n```bash\n$ pip install aws-coco\n```\n\nUsage\n\n```bash\n$ coco -c green -i fingerprint\n```\n\nYou should now have a new browser tab with your aws session!\n\nContinue reading for a more in-depth walkthrough of the setup.\n\n## Requirements\n\n- [Firefox](https://www.mozilla.org/en-US/firefox/new/)\n- [Firefox Multi-Account Containers](https://addons.mozilla.org/en-US/firefox/addon/multi-account-containers/)\n- [Open URL in Container Extension](https://addons.mozilla.org/en-US/firefox/addon/open-url-in-container/)\n- [Python >= 3.7](http://python.org/)\n\nIf you don't wish to install the extension through the marketplace, the source for the extension can be found [here](https://github.com/honsiorovskyi/open-url-in-container).\n\n## Installation\n\n```bash\n$ pip install aws_coco\n```\n\n## Usage\n\nThis section explains how to use `coco` and covers some of the options available to you.\n\n### Basic Usage\n\n```bash\n$ coco --color green --icon fingerprint --name test\n```\n\nThis will open the url in a `green` firefox container tab named `test` with a `fingerprint` icon.\n\n### Credential Resolution\n\nThis project uses [boto3](https://github.com/boto/boto3). You can learn more about how `boto3` resolves credentials [here](https://boto3.amazonaws.com/v1/documentation/api/1.9.42/guide/configuration.html#configuring-credentials).\n\nIf you specify the `--profile` flag, `coco` will pass that value into the `boto3` session and it will attempt to use the corresponding section in the `~/.aws/credentials` file for the session.\n\n### Options\n\nThis section contains a description of the various options available to you. You can also pass the `-h` flag to print the help.\n\n|Flag|Description|Default|Required|\n|----|-----------|-------|--------|\n|`--color`, `-c`|The container tab's color||false|\n|`--container`, `--no-container`|Determines if the url should be opened in a firefox container||true|\n|`--destination`, `-d`|The destination URL to open in the AWS console||false|\n|`--icon`, `-i`|The container tab's icon||false|\n|`--name`, `-n`|The container tab's name|The profile name if passed|false|\n|`--open`, `--no-open`|Determines if the url should be automatically opened in the browser||true|\n|`--profile`, `-p`|The AWS profile to use||false|\n\n### Available Colors\n|value|\n|-----|\n|blue|\n|turquoise|\n|green|\n|yellow|\n|orange|\n|red|\n|pink|\n|purple|\n\n### Available Icons\n|value|\n|-----|\n|fingerprint|\n|briefcase|\n|dollar|\n|cart|\n|vacation|\n|gift|\n|food|\n|fruit|\n|pet|\n|tree|\n|chill|\n|circle|\n|fence|\n\n## Development\n\n```bash\n$ git clone https://github.com/wulfmann/aws-coco.git\n$ git clone git@github.com:wulfmann/aws-coco.git\n```\n\nInstall Dependencies\n\n```bash\n$ poetry install\n```\n\nRun the command\n\n```bash\n$ poetry run coco -c green -i fingerprint\n```\n\nRun tests\n\n```bash\n$ poetry run pytest\n```\n",
    'author': 'Joe Snell',
    'author_email': 'joepsnell@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wulfmann/aws-coco',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
