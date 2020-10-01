import os
import setuptools
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

with open("README.md", "r") as _file:
    readme = _file.read()

class PostDevCmd(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        print('test dev')


class PostInstallCmd(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        print('install test')

setuptools.setup(
    name="appchance",
    version="0.1.1",
    author="Radosław Przytuła",
    author_email="radoslaw.przytula@appchance.com",
    description="In Appchance we trust",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/appchance/pychance/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.7',
    cmdclass={
        'develop': PostDevCmd,
        'install': PostInstallCmd,
    },
)
