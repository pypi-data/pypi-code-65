import os
import sys

import setuptools

with open("README.md", "r") as _file:
    readme = _file.read()

setuptools.setup(
    name="appchance",
    version="0.3.0",
    author="Appchance Spellbook",
    author_email="backend@appchance.com",
    description="Appchance's spellbook for wizards and ninjas. Useful in dungeons.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/appchance/pychance/",
    packages=setuptools.find_packages(),
    install_requires=["doit", "django", "cookiecutter", "ipython"],
    scripts=["bin/dodo"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django :: 3.0",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.7",
)
