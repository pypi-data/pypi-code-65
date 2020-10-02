#!/usr/bin/env python

from setuptools import setup, find_namespace_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    author="Stream Machine B.V.",
    author_email='apis@streammachine.io',
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
    ],
    description="Common Schema components for Stream Machine driver",
    install_requires=[],
    long_description=readme,
    include_package_data=True,
    keywords='streammachine schema-common client driver',
    name='streammachine-schemas-common',
    packages=find_namespace_packages(include=['streammachine.schemas.*']),
    setup_requires=[],
    version='0.0.3',
    zip_safe=False,
)
