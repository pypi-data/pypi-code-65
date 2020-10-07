# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fs', 'fs.googledrivefs']

package_data = \
{'': ['*']}

install_requires = \
['fs>=2.4.10', 'google-api-python-client>=1.6.3', 'google-auth>=1.5.1']

entry_points = \
{'fs.opener': ['googledrive = fs.googledrivefs.opener:GoogleDriveFSOpener']}

setup_kwargs = {
    'name': 'fs.googledrivefs',
    'version': '2.0.0',
    'description': 'Pyfilesystem2 implementation for Google Drive',
    'long_description': '# fs.googledrivefs\n\n![image](https://github.com/rkhwaja/fs.googledrivefs/workflows/ci/badge.svg) [![Coverage report](https://coveralls.io/repos/github/rkhwaja/fs.googledrivefs/badge.svg?branch=master "Coverage summary")](https://coveralls.io/github/rkhwaja/fs.googledrivefs?branch=master) [![PyPI version](https://badge.fury.io/py/fs.googledrivefs.svg)](https://badge.fury.io/py/fs.googledrivefs)\n\nImplementation of [pyfilesystem2](https://docs.pyfilesystem.org/) file system for Google Drive\n\n# Installation\n\n```bash\n  pip install fs.googledrivefs\n```\n\n# Usage\n\n```python\n  from google.oauth2.credentials import Credentials\n  from fs.googledrivefs import GoogleDriveFS\n\n  credentials = Credentials(oauth2_access_token,\n    refresh_token=oauth2_refresh_token,\n    token_uri="https://www.googleapis.com/oauth2/v4/token",\n    client_id=oauth2_client_id,\n    client_secret=oauth2_client_secret)\n\n  fs = GoogleDriveFS(credentials=credentials)\n\n  # fs is now a standard pyfilesystem2 file system, alternatively you can use the opener...\n\n  from fs.opener import open_fs\n\n  fs2 = open_fs("googledrive:///?access_token=<oauth2 access token>&refresh_token=<oauth2 refresh token>&client_id=<oauth2 client id>&client_secret=<oauth2 client secret>")\n\n  # fs2 is now a standard pyfilesystem2 file system\n```\n\n## Default Google Authentication\n\nIf your application is accessing the Google Drive API as a \n[GCP Service Account](https://cloud.google.com/iam/docs/service-accounts), `fs.googledrivefs` will\ndefault to authenticating using the Service Account credentials specified by the \n[`GOOGLE_APPLICATION_CREDENTIALS` environment variable](https://cloud.google.com/docs/authentication/getting-started). \nThis can greatly simplify the URLs used by the opener:\n\n```python\n  from fs.opener import open_fs\n\n  fs2 = open_fs("googledrive:///required/path")\n```\n\nYou can also use the same method of authentication when using `GoogleDriveFS` directly:\n\n```python\n  import google.auth\n  from fs.googledrivefs import GoogleDriveFS\n\n  credentials, _ = google.auth.default()\n  fs = GoogleDriveFS(credentials=credentials)\n```\n\n## Using `fs.googledrivefs` with an organisation\'s Google Account\n\nWhile access to the Google Drive API is straightforward to enable for a personal Google Account,\na user of an organisation\'s Google Account will typically only be able to enable an API in the\ncontext of a\n[GCP Project](https://cloud.google.com/resource-manager/docs/creating-managing-projects).\nThe user can then configure a \n[Service Account](https://cloud.google.com/iam/docs/understanding-service-accounts)\nto access all or a sub-set of the user\'s files using `fs.googledrivefs` with the following steps:\n\n- create a GCP Project\n- enable the Google Drive API for that Project\n- create a Service Account for that Project\n- share any Drive directory (or file) with that Service Account (using the accounts email)\n\n## Notes on forming `fs` urls for GCP Service Accounts\n\nSay that your is drive is structured as follows:\n\n```\n/alldata\n  /data1\n  /data2\n   :\n```\n\nAlso say that you have given your application\'s service account access to everything in `data1`.\nIf your application opens url `/alldata/data1` using `fs.opener.open_fs()`, then `fs.googledrivefs`\nmust first get the info for `alldata` to which it has no access and so the operation fails. \n\nTo address this we can tell `fs.googledrivefs` to treat `data1` as the root directory by supplying\nthe file id of `data1` as the request parameter `root_id`. The fs url you would now use is\n`googledrive:///?root_id=12345678901234567890`: \n\n```python\n  from fs.opener import open_fs\n\n  fs2 = open_fs("googledrive:///?root_id=12345678901234567890")\n```\n\nYou can also use the `rootId` when using `GoogleDriveFS` directly:\n\n```python\n  import google.auth\n  from fs.googledrivefs import GoogleDriveFS\n\n  credentials, _ = google.auth.default()\n  fs = GoogleDriveFS(credentials=credentials, rootId="12345678901234567890")\n```\n\nNote that any file or directory\'s id is readily accessible from it\'s web url.\n\n# Development\n\nTo run the tests, set the following environment variables:\n\n- GOOGLEDRIVEFS_TEST_CLIENT_ID - your client id (see Google Developer Console)\n- GOOGLEDRIVEFS_TEST_CLIENT_SECRET - your client secret (see Google Developer Console)\n- GOOGLEDRIVEFS_TEST_CREDENTIALS_PATH - path to a json file which will contain the credentials\n\nThen generate the credentials json file by running\n\n```bash\n  python tests/generate-credentials.py\n```\n\nThen run the tests by executing\n\n```bash\n  pytest\n```\n\nin the root directory\n(note that if `GOOGLEDRIVEFS_TEST_CREDENTIALS_PATH` isn\'t set \nthen the test suite will try to use the default Google credentials).\nThe tests may take an hour or two to complete.\nThey create and destroy many, many files and directories\nmostly under the /test-googledrivefs directory in the user\'s Google Drive\nand a few in the root directory\n\nNote that, if your tests are run using a service account,\nyou can set the root id using `GOOGLEDRIVEFS_TEST_ROOT_ID`.\n',
    'author': 'Rehan Khwaja',
    'author_email': 'rehan@khwaja.name',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rkhwaja/fs.googledrivefs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
