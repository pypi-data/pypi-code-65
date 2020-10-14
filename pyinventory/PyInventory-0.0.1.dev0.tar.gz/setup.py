# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['inventory',
 'inventory.admin',
 'inventory.gpx_tools',
 'inventory.management',
 'inventory.management.commands',
 'inventory.managers',
 'inventory.migrations',
 'inventory.models',
 'inventory.selectors',
 'inventory.services',
 'inventory.signal_handlers',
 'inventory.tests',
 'inventory_project',
 'inventory_project.for_runners_helper_app',
 'inventory_project.for_runners_helper_app.fixtures',
 'inventory_project.for_runners_helper_app.management',
 'inventory_project.for_runners_helper_app.management.commands',
 'inventory_project.utils',
 'inventory_tests']

package_data = \
{'': ['*'],
 'inventory': ['static/*',
               'static/chartjs/*',
               'static/dygraphs/*',
               'static/leaflet/*',
               'static/leaflet/images/*',
               'templates/admin/for_runners/*',
               'templates/admin/for_runners/eventmodel/*',
               'templates/admin/for_runners/gpxmodel/*',
               'templates/admin/for_runners/gpxmodel/include/*',
               'templates/for_runners/*',
               'templates/for_runners/includes/*'],
 'inventory.tests': ['fixture_files/*'],
 'inventory_project': ['templates/*', 'templates/admin/*']}

install_requires = \
['colorama',
 'colorlog',
 'django-debug-toolbar',
 'django-import-export',
 'django>=2.2.0,<2.3.0',
 'gunicorn']

entry_points = \
{'console_scripts': ['inventory = inventory_project.cli:cli',
                     'manage = inventory_project.__main__:manage',
                     'publish = inventory_project.publish:publish',
                     'update_rst_readme = '
                     'inventory_project.publish:update_readme']}

setup_kwargs = {
    'name': 'pyinventory',
    'version': '0.0.1.dev0',
    'description': 'Web based management to catalog things including state and location etc. using Python/Django.',
    'long_description': '===========\nPyInventory\n===========\n\nWeb based management to catalog things including state and location etc. using Python/Django.\n\nCurrent status: Just start the project. Nothing is done, nothing is useable, yet ;)\n\nPull requests welcome!\n\n+-----------------------------------+-------------------------------------------------+\n| |Build Status on github|          | `github.com/jedie/PyInventory/actions`_         |\n+-----------------------------------+-------------------------------------------------+\n| |Build Status on travis-ci.org|   | `travis-ci.org/jedie/PyInventory`_              |\n+-----------------------------------+-------------------------------------------------+\n| |Coverage Status on codecov.io|   | `codecov.io/gh/jedie/PyInventory`_              |\n+-----------------------------------+-------------------------------------------------+\n| |Coverage Status on coveralls.io| | `coveralls.io/r/jedie/PyInventory`_             |\n+-----------------------------------+-------------------------------------------------+\n| |Status on landscape.io|          | `landscape.io/github/jedie/PyInventory/master`_ |\n+-----------------------------------+-------------------------------------------------+\n\n.. |Build Status on github| image:: https://github.com/jedie/PyInventory/workflows/test/badge.svg?branch=master\n.. _github.com/jedie/PyInventory/actions: https://github.com/jedie/PyInventory/actions\n.. |Build Status on travis-ci.org| image:: https://travis-ci.org/jedie/PyInventory.svg\n.. _travis-ci.org/jedie/PyInventory: https://travis-ci.org/jedie/PyInventory/\n.. |Coverage Status on codecov.io| image:: https://codecov.io/gh/jedie/PyInventory/branch/master/graph/badge.svg\n.. _codecov.io/gh/jedie/PyInventory: https://codecov.io/gh/jedie/PyInventory\n.. |Coverage Status on coveralls.io| image:: https://coveralls.io/repos/jedie/PyInventory/badge.svg\n.. _coveralls.io/r/jedie/PyInventory: https://coveralls.io/r/jedie/PyInventory\n.. |Status on landscape.io| image:: https://landscape.io/github/jedie/PyInventory/master/landscape.svg\n.. _landscape.io/github/jedie/PyInventory/master: https://landscape.io/github/jedie/PyInventory/master\n\n-------\ninstall\n-------\n\ntbd\n\n::\n\n    ~$ git clone https://github.com/jedie/PyInventory.git\n    ~$ cd PyInventory\n    ~/PyInventory$ make\n    help                 List all commands\n    install-poetry       install or update poetry\n    install              install PyInventory via poetry\n    update               update the sources and installation\n    lint                 Run code formatters and linter\n    fix-code-style       Fix code formatting\n    tox-listenvs         List all tox test environments\n    tox                  Run pytest via tox with all environments\n    tox-py36             Run pytest via tox with *python v3.6*\n    tox-py37             Run pytest via tox with *python v3.7*\n    tox-py38             Run pytest via tox with *python v3.8*\n    pytest               Run pytest\n    update-rst-readme    update README.rst from README.creole\n    publish              Release new version to PyPi\n    run-dev-server       Run the django dev server in endless loop.\n    run-server           Run the gunicorn server in endless loop.\n    backup               Backup everything\n    create-starter       Create starter file.\n    ~/PyInventory$ make install\n    ...\n\n------------------------------\nBackwards-incompatible changes\n------------------------------\n\nNothing, yet ;)\n\n-------\nhistory\n-------\n\n* `compare v0.0.1...master <https://github.com/jedie/PyInventory/compare/v0.0.1...master>`_ **dev** \n\n    * tbc\n\n* v0.0.1 - 14.10.2020\n\n    * Just create a pre-alpha release to save the PyPi package name ;)\n\n-----\nlinks\n-----\n\n+----------+------------------------------------------+\n| Homepage | `http://github.com/jedie/PyInventory`_   |\n+----------+------------------------------------------+\n| PyPi     | `https://pypi.org/project/PyInventory/`_ |\n+----------+------------------------------------------+\n\n.. _http://github.com/jedie/PyInventory: http://github.com/jedie/PyInventory\n.. _https://pypi.org/project/PyInventory/: https://pypi.org/project/PyInventory/\n\n--------\ndonation\n--------\n\n* `paypal.me/JensDiemer <https://www.paypal.me/JensDiemer>`_\n\n* `Flattr This! <https://flattr.com/submit/auto?uid=jedie&url=https%3A%2F%2Fgithub.com%2Fjedie%2FPyInventory%2F>`_\n\n* Send `Bitcoins <http://www.bitcoin.org/>`_ to `1823RZ5Md1Q2X5aSXRC5LRPcYdveCiVX6F <https://blockexplorer.com/address/1823RZ5Md1Q2X5aSXRC5LRPcYdveCiVX6F>`_\n\n------------\n\n``Note: this file is generated from README.creole 2020-10-14 10:06:00 with "python-creole"``',
    'author': 'JensDiemer',
    'author_email': 'git@jensdiemer.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
