# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['python_lifecycle_training',
 'python_lifecycle_training.calculator',
 'tests',
 'tests.calculator']

package_data = \
{'': ['*']}

install_requires = \
['dynaconf>=3.1.2,<4.0.0', 'fire>=0.3.1,<0.4.0', 'loguru>=0.5.3,<0.6.0']

entry_points = \
{'console_scripts': ['calc = python_lifecycle_training.calculator.cli:main']}

setup_kwargs = {
    'name': 'python-lifecycle-training',
    'version': '0.1.2',
    'description': 'A training program to learn the Python Development Cycle',
    'long_description': '=========================\nPython Lifecycle Training\n=========================\n\n.. image:: https://github.com/sp-fm/python-lifecycle-training/workflows/Tests/badge.svg\n    :target: https://github.com/sp-fm/python-lifecycle-training/actions?query=workflow%3ATests\n    :alt: Tests\n\n.. image:: https://github.com/sp-fm/python-lifecycle-training/workflows/Documentation/badge.svg\n    :target: https://sp-fm.github.io/python-lifecycle-training/\n    :alt: Documentation\n\n.. image:: https://github.com/sp-fm/python-lifecycle-training/workflows/Release/badge.svg\n    :target: https://pypi.python.org/pypi/python-lifecycle-training\n    :alt: Release\n\n.. image:: https://img.shields.io/pypi/v/python-lifecycle-training.svg\n    :target: https://pypi.python.org/pypi/python-lifecycle-training\n    :alt: PyPi Version\n\nA training program on getting to know the Python Development Cycle from project setup\nall the way to project deployment.\n\n* **Source Code**: https://github.com/sp-fm/python-lifecycle-training\n* **Documentation**: https://sp-fm.github.io/python-lifecycle-training/\n* **Bug Reports**: https://github.com/sp-fm/python-lifecycle-training/issues\n\nSyllabus\n--------\n\nProject Initialization\n~~~~~~~~~~~~~~~~~~~~~~\n\n* editorconfig_\n* flake8_\n* black_\n* isort_\n* mypy_\n* pre-commit_\n\nProject Setup\n~~~~~~~~~~~~~\n\n* fire_\n* loguru_\n* dynaconf_\n* pytest_\n* coverage_\n* pytest-cov_\n* tox_\n\nProject Deployment\n~~~~~~~~~~~~~~~~~~\n\n* sphinx_\n* gh-actions_\n* gh-pages_\n* pypi_\n\nFor more information check out the full tutorial_.\n\nYou can find the template for all the tools mentioned in this training at\nhttps://github.com/sp-fm/fuse-framework which can be used as follows:\n\n.. code-block:: console\n\n    $ cookiecutter gh:sp-fm/fuse-framework\n\nHope you enjoy this training.\n\n.. _editorconfig: https://sp-fm.github.io/python-lifecycle-training/editorconfig.html\n.. _flake8: https://sp-fm.github.io/python-lifecycle-training/flake8.html\n.. _black: https://sp-fm.github.io/python-lifecycle-training/black.html\n.. _isort: https://sp-fm.github.io/python-lifecycle-training/isort.html\n.. _mypy: https://sp-fm.github.io/python-lifecycle-training/mypy.html\n.. _pre-commit: https://sp-fm.github.io/python-lifecycle-training/pre-commit.html\n.. _fire: https://sp-fm.github.io/python-lifecycle-training/fire.html\n.. _loguru: https://sp-fm.github.io/python-lifecycle-training/loguru.html\n.. _dynaconf: https://sp-fm.github.io/python-lifecycle-training/dynaconf.html\n.. _pytest: https://sp-fm.github.io/python-lifecycle-training/pytest.html\n.. _coverage: https://sp-fm.github.io/python-lifecycle-training/coverage.html\n.. _pytest-cov: https://sp-fm.github.io/python-lifecycle-training/pytest-cov.html\n.. _tox: https://sp-fm.github.io/python-lifecycle-training/tox.html\n.. _sphinx: https://sp-fm.github.io/python-lifecycle-training/sphinx.html\n.. _gh-actions: https://sp-fm.github.io/python-lifecycle-training/gh-actions.html\n.. _gh-pages: https://sp-fm.github.io/python-lifecycle-training/gh-pages.html\n.. _pypi: https://sp-fm.github.io/python-lifecycle-training/pypi.html\n.. _tutorial: https://sp-fm.github.io/python-lifecycle-training/tutorial.html\n',
    'author': 'Shashanka Prajapati',
    'author_email': 'shashanka@fusemachines.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sp-fm/python-lifecycle-training',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
