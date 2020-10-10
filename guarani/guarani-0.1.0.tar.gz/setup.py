# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['guarani',
 'guarani.jose',
 'guarani.jose.jwk',
 'guarani.jose.jws',
 'guarani.jose.jwt',
 'guarani.oauth2',
 'guarani.oauth2.authentication',
 'guarani.oauth2.endpoints',
 'guarani.oauth2.grants',
 'guarani.oauth2.integrations']

package_data = \
{'': ['*']}

install_requires = \
['cryptography>=3.1.1,<4.0.0']

setup_kwargs = {
    'name': 'guarani',
    'version': '0.1.0',
    'description': 'Modern web protocols for authentication, authorization and identity in Python.',
    'long_description': '# Project Guarani\n\nThis library provides an implementation for authentication and authorization\nof web applications. It provides support for JWTs, OAuth 2.1 and (soon) OpenID Connect.\n\nFor more details on each feature, please visit the respective documentation.\n\nAny doubts and suggestions can be sent to my [email](mailto:eduardorbr7@gmail.com).\nJust prepend the title with `#Guarani#`, and I will try my best to answer.\n\n# License\n\nThis project is licensed under the MIT License.\nFor more details, please refer to the `LICENSE` file.\n',
    'author': 'Eduardo Ribeiro Rezende',
    'author_email': 'eduardorbr7@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/revensky/guarani',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
