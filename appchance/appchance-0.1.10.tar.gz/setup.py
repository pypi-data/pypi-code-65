import os, sys
import setuptools

with open("README.md", "r") as _file:
    readme = _file.read()

setuptools.setup(
    name="appchance",
    version="0.1.10",
    author="Appchance Backend Special Forces Team",
    author_email="backend@appchance.com",
    description="Toolbelt for wizards and ninjas.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/appchance/pychance/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django :: 3.0",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 2 - Pre-Alpha",
        "Operating System :: POSIX :: Linux"
    ],
    python_requires='>=3.7',
)
