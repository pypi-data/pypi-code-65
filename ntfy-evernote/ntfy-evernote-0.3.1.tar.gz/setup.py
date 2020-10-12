# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['ntfy_evernote']
install_requires = \
['evernote3>=1.25.14,<2.0.0', 'oauth2>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'ntfy-evernote',
    'version': '0.3.1',
    'description': 'Evernote backend for ntfy',
    'long_description': "# ntfy-evernote\n\nEvernote backend for ntfy.\n\n**Currently only work on sandbox.**\n\n## Usage\n\n``` yaml\nntfy_evernote:\n    access_token: ...\n    china: false\n```\n\n*If you don't provide the access token, a login guide will auto start.*\n\nRequired parameters:\n\n- `access_token` - string, the access token grant from evernote.\n\nOptional parameters:\n\n- `notebook` - string, name of the notebook to push message.\n- `sandbox` - bool.\n- `china` - bool, is in china.\n",
    'author': 'Cologler',
    'author_email': 'skyoflw@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Cologler/ntfy-evernote-python',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
