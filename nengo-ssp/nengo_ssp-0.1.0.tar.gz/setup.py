#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['numpy==1.18.5','nengo','nengo_spa==1.0.1', ]

setup_requirements = [ ]

test_requirements = ['numpy', 'nengo']

setup(
    author="Nicole Sandra-Yaffa Dumont",
    author_email='nicole.s.dumont@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Spatial Semantic Pointers (SSPs) for nengo and nengo_spa. Grid cell SSPs included.",
    entry_points={
        'console_scripts': [
            'nengo_ssp=nengo_ssp.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='nengo_ssp',
    name='nengo_ssp',
    packages=find_packages(include=['nengo_ssp', 'nengo_ssp.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/nsdumont/nengo_ssp',
    version='0.1.0',
    zip_safe=False,
)
