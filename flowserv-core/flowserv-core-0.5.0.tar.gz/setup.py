# This file is part of the Reproducible and Reusable Data Analysis Workflow
# Server (flowServ).
#
# Copyright (C) 2019-2020 NYU.
#
# flowServ is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

import os
import re

from setuptools import setup, find_packages


"""Required packages for install, test, docs, and tests."""

install_requires = [
    'docker',
    'gitpython',
    'passlib',
    'psycopg2-binary',
    'python-dateutil',
    'pyyaml>=5.1',
    'requests',
    'SQLAlchemy>=1.3.18',
    'Click',
    'boto3'
]


tests_require = [
    'coverage>=4.0',
    'pytest',
    'pytest-cov',
    'tox'
]


extras_require = {
    'docs': [
        'Sphinx',
        'sphinx-rtd-theme'
    ],
    'tests': tests_require,
}


# Get the version string from the version.py file in the flowserv package.
# Based on:
# https://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package
with open(os.path.join('flowserv', 'version.py'), 'rt') as f:
    filecontent = f.read()
match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", filecontent, re.M)
if match is not None:
    version = match.group(1)
else:
    raise RuntimeError('unable to find version string in %s.' % (filecontent,))


# Get long project description text from the README.rst file
with open('README.rst', 'rt') as f:
    readme = f.read()

description = (
    'Reproducible and Reusable Data Analysis Workflow Server '
    '(Core Infrastructure)'
)
setup(
    name='flowserv-core',
    version=version,
    description=description,
    long_description=readme,
    long_description_content_type='text/x-rst',
    keywords='reproducibility workflows benchmarks data-analysis',
    url='https://github.com/scailfin/flowserv-core',
    author='Heiko Mueller',
    author_email='heiko.muller@gmail.com',
    license='MIT',
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    extras_require=extras_require,
    tests_require=tests_require,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'flowserv = flowserv.cli.admin:cli'
        ]
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python'
    ]
)
