# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mail_deduplicate', 'mail_deduplicate.tests']

package_data = \
{'': ['*']}

install_requires = \
['boltons>=20.2.1,<21.0.0',
 'click-log>=0.3.2,<0.4.0',
 'click>=7.1.2,<8.0.0',
 'tabulate>=0.8.7,<0.9.0']

extras_require = \
{'docs': ['sphinx>=3.2.1,<4.0.0', 'sphinx_rtd_theme>=0.5.0,<0.6.0']}

entry_points = \
{'console_scripts': ['mdedup = mail_deduplicate.cli:mdedup']}

setup_kwargs = {
    'name': 'mail-deduplicate',
    'version': '5.1.0',
    'description': 'Deduplicate mails from mbox files and maildir folders.',
    'long_description': 'Mail Deduplicate\n================\n\nCommand-line tool to deduplicate mails from a set of mbox files and/or maildir\nfolders.\n\nStable release: |release| |versions| |license| |dependencies|\n\nDevelopment: |build| |docs| |coverage| |quality|\n\n.. |release| image:: https://img.shields.io/pypi/v/mail-deduplicate.svg\n    :target: https://pypi.python.org/pypi/mail-deduplicate\n    :alt: Last release\n.. |versions| image:: https://img.shields.io/pypi/pyversions/mail-deduplicate.svg\n    :target: https://pypi.python.org/pypi/mail-deduplicate\n    :alt: Python versions\n.. |license| image:: https://img.shields.io/pypi/l/mail-deduplicate.svg\n    :target: https://www.gnu.org/licenses/gpl-2.0.html\n    :alt: Software license\n.. |dependencies| image:: https://requires.io/github/kdeldycke/mail-deduplicate/requirements.svg?branch=main\n    :target: https://requires.io/github/kdeldycke/mail-deduplicate/requirements/?branch=main\n    :alt: Requirements freshness\n.. |build| image:: https://travis-ci.org/kdeldycke/mail-deduplicate.svg?branch=develop\n    :target: https://travis-ci.org/kdeldycke/mail-deduplicate\n    :alt: Unit-tests status\n.. |docs| image:: https://readthedocs.org/projects/maildir-deduplicate/badge/?version=develop\n    :target: https://maildir-deduplicate.readthedocs.io/en/develop/\n    :alt: Documentation Status\n.. |coverage| image:: https://codecov.io/gh/kdeldycke/mail-deduplicate/branch/develop/graph/badge.svg\n    :target: https://codecov.io/github/kdeldycke/mail-deduplicate?branch=develop\n    :alt: Coverage Status\n.. |quality| image:: https://scrutinizer-ci.com/g/kdeldycke/mail-deduplicate/badges/quality-score.png?b=develop\n    :target: https://scrutinizer-ci.com/g/kdeldycke/mail-deduplicate/?branch=develop\n    :alt: Code Quality\n\n\nFeatures\n--------\n\n* Duplicate detection based on cherry-picked mail headers.\n* Source mails from multiple mbox files and/or maildir folders.\n* Multiple removal strategies based on size, timestamp or file path.\n* Dry-run mode.\n* Protection against false-positives by checking for size and content\n  differences.\n\n\nInstallation\n------------\n\nThis package is `available on PyPi\n<https://pypi.python.org/pypi/mail-deduplicate>`_, so you can install the\nlatest stable release and its dependencies with a simple ``pip`` call:\n\n.. code-block:: shell-session\n\n    $ pip install mail-deduplicate\n\n\nDocumentation\n-------------\n\nDocs are `hosted on Read the Docs\n<https://maildir-deduplicate.readthedocs.io>`_.\n',
    'author': 'Kevin Deldycke',
    'author_email': 'kevin@deldycke.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kdeldycke/mail-deduplicate',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
