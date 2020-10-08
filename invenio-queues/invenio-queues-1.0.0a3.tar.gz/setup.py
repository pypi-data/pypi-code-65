# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for managing queues."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'pytest-invenio>=1.4.0',
]

extras_require = {
    'docs': [
        'Sphinx>=3',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = []

install_requires = [
    'invenio-base>=1.2.2',
    'invenio-celery>=1.2.0',
    'redis>=3.2.1',
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_queues', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-queues',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio TODO',
    license='MIT',
    author='CERN',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/invenio-queues',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'flask.commands': [
            'queues = invenio_queues.cli:queues',
        ],
        'invenio_base.apps': [
            'invenio_queues = invenio_queues:InvenioQueues',
        ],
        'invenio_base.api_apps': [
            'invenio_queues = invenio_queues:InvenioQueues',
        ],
        'invenio_i18n.translations': [
            'messages = invenio_queues',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
