import os
import sys

import setuptools


setuptools.setup(
    name="appchance",
    version="0.3.1.0",
    author="Appchance Backend Spellbook",
    author_email="backend@appchance.com",
    description="Appchance's spellbook for wizards and ninjas. Useful in dungeons.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/appchance/pychance/",
    packages=setuptools.find_packages(),
    install_requires=["doit", "django", "cookiecutter", "ipython", "swapper"],
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
