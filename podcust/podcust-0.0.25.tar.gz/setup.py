#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages
import os
# Needs pip>=20
from pip._internal.network.session import PipSession
from pip._internal.req import parse_requirements

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()
# adapted from:
# https://stackoverflow.com/a/57191701
# https://stackoverflow.com/a/59969843
# https://alexanderwaldin.github.io/packaging-python-project.html
requirements0 = parse_requirements(
    os.path.join(os.path.dirname(__file__), 'requirements.txt'),
    session=PipSession()
)
requirements = [str(requirement.requirement) for requirement in requirements0]
del requirements0


setup_requirements = [
    "pip>=20.2",
    "bump2version>=1.0",
    "wheel>=0.35.1",
    "Sphinx>=3.2.1",
    "twine>=3.2.0",
    "check-manifest"
]

test_requirements = [
    'pytest',
    'pytest-runner',
    "mock",
    "flake8",
    "black",
    "mypy",
    "tox",
    "coverage",
    "yamllint",
    "doc8"
]

setup(
    author="Nikolaos Perrakis",
    author_email='nikperrakis@gmail.com',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    description="Python utility to handle podman containers within Fedora.",
    entry_points={
        'console_scripts': [
            'podcust=podcust.cli:main',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='podcust',
    name='podcust',
    packages=find_packages(include=['podcust', 'podcust.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    # hack from https://stackoverflow.com/a/41398850/1904901 to be able to install deps from pip
    extras_require={
        "dev": setup_requirements + test_requirements
    },
    url='https://github.com/Iolaum/podcust',
    version='0.0.25',
    zip_safe=False,
)
