# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['broadworks_ocip']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=20.2.0,<21.0.0', 'classforge>=0.92,<0.93', 'lxml>=4.5.2,<5.0.0']

setup_kwargs = {
    'name': 'broadworks-ocip',
    'version': '1.0.1',
    'description': 'API interface to the OCI-P provisioning interface of a Broadworks softswitch',
    'long_description': '==========================\nBroadworks OCI-P Interface\n==========================\n\n\n.. image:: https://img.shields.io/pypi/v/broadworks_ocip.svg\n        :target: https://pypi.python.org/pypi/broadworks_ocip\n\n.. image:: https://img.shields.io/travis/nigelm/broadworks_ocip.svg\n        :target: https://travis-ci.com/nigelm/broadworks_ocip\n\n.. image:: https://readthedocs.org/projects/broadworks-ocip/badge/?version=latest\n        :target: https://broadworks-ocip.readthedocs.io/en/latest/?badge=latest\n        :alt: Documentation Status\n\n\n\n\nInterfaces to the OCI-P provisioning interface of a Broadworks softswitch\n\n\n* Free software: BSD license\n* Documentation: https://broadworks-ocip.readthedocs.io.\n\n\nFeatures\n--------\n\n* python objects to match all Broadworks schema objects\n* API framework to talk to a Broadworks server\n* additional magic to handle authentication and sessions\n* Based on Broadworks schema R21\n\n\nUsage\n-----\n\nMore details is given within the usage section of the documentation, but the\nminimal summary is::\n\n    from broadworks_ocip import BroadworksAPI\n\n    # configure the API, connect and authenticate to the server\n    api = BroadworksAPI(\n        host=args.host, port=args.port, username=args.username, password=args.password,\n    )\n\n    # get the platform software level\n    response = api.command("SystemSoftwareVersionGetRequest")\n    print(response.version)\n\n\nCredits\n-------\n\nThe class is built using Michael DeHaan\'s `ClassForge`_ object system.\n\nThis package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.\n\n.. _ClassForge: https://classforge.io/\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage\n',
    'author': 'Nigel Metheringham',
    'author_email': 'nigelm@cpan.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/broadworks-ocip/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
