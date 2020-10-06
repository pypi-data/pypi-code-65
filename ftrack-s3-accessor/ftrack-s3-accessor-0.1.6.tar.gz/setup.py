# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ftrack_s3_accessor']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.15.10,<2.0.0',
 'ftrack-action-handler>=0.2.1,<0.3.0',
 'ftrack-python-api>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'ftrack-s3-accessor',
    'version': '0.1.6',
    'description': 'A ftrack s3 accessor updated to work with ftrack-python-api and boto3.',
    'long_description': "# ftrack-s3-accessor\n\nAn ftrack s3 accessor updated to work with ftrack-python-api and boto3. \n\n## Requirements: \n- boto3 - if used standalone \n- ftrack-action-handler (optional) - if used with the transfer components action found [here](https://bitbucket.org/!api/2.0/snippets/ftrack/B6dX/f9e89e8bf95065a6fc0541dd058863ff1ddaceb6/files/transfer_components_action.py)\n\n## Installation\n\nInstall using pip:\n    \n    pip install ftrack-s3-accessor\n\n## Configuration\n\nConfigure a new location within ftrack with the name 'studio.remote'. This will be used as the location for s3.\n\nCreate a storage bucket in s3 and set the bucket name using the FTRACK_S3_ACCESSOR_BUCKET environment variable (default: ftrack). Ensure your bucket name is globally unique and meets aws s3 naming restrictions.\n\nSet all other ftrack environment variables for your ftrack instance.\n\nRunning the scripts from within your environment requires you to additionally set your sources root to the accessor directory.\n\n    PYTHONPATH=./ftrack_s3_accessor\n\nEnsure you have an working aws configuration under your ~/.aws folder. You can check this by running:\n    \n    import boto3\n\nIf this fails, your aws configuration isn't setup properly. Refer to the [boto3](https://github.com/boto/boto3) documentation on how to set it up. You should only need a ~/.aws/config and ~/.aws/credentials file.\n\n## Usage\n\nThe main plugin can be found in the plugins folder. This folder may be registered using the FTRACK_EVENT_PLUGIN_PATH ftrack environment variable so that it is picked up when ftrack is started.\n\nExamples of how to use the plugin can be found in the scripts folder. The simplest way to launch ftrack with the accessor is scripts/start_ftrack_with_s3.py. \n\nIt is possible to use the [transfer components](https://bitbucket.org/!api/2.0/snippets/ftrack/B6dX/f9e89e8bf95065a6fc0541dd058863ff1ddaceb6/files/transfer_components_action.py) action to move components between local and remote storage. Ensure it is on the FTRACK_EVENT_PLUGIN_PATH (or add it to the plugins folder) and it should become available under ftracks actions menu. You will need to ensure your local storage is also correctly configured within a script when running the accessor outside of ftrack-connect, as the connect location configured by the desktop client will not be available as an option.\n",
    'author': 'Ian Wootten',
    'author_email': 'hi@niftydigits.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/niftydigits/ftrack-s3-accessor',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*, !=3.7.*',
}


setup(**setup_kwargs)
