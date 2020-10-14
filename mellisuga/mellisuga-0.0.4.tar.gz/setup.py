#!/usr/bin/env python
from setuptools import setup, find_packages


with open('README.md') as readme_file:
    README = readme_file.read()


setup(
    name='mellisuga',
    version='0.0.4',
    description="AWS Lambda Microframework",
    long_description=README,
    author="Johannes Zuendel",
    author_email='jozuendel@gmail.com',
    url='https://gitlab.com/Zuendel/mellisuga',
    packages=find_packages(exclude=['tests']),
    license="Apache License 2.0",
    package_data={'mellisuga': ['*.json']},
    include_package_data=True,
    zip_safe=False,
    keywords='mellisuga aws labmda microframework websocket',
)
