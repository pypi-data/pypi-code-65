#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The setup script."""
from setuptools import find_packages
from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = []

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Vedad Ramovic",
    author_email='vedad@socialexplorer.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
    ],
    description="Tools for data team at SE.",
    entry_points={
        'console_scripts': [
            'sedatatools=sedatatools.cli:main',
        ],
    },
    scripts=[],
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='sedatatools',
    name='sedatatools',
    packages=find_packages(),  # include=['sedatatools']
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/SocialExplorer/ContentProduction/tree/master/sedatatools',
    version='1.0.4',
    zip_safe=False,
        python_requires='>=3.8',
)
