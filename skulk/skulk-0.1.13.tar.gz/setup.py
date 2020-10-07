#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import setuptools
from setuptools.command.build_py import build_py

NAME = "skulk"
DESCRIPTION = "Streamline release for Conductor client tools and others"
HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, 'VERSION')) as version_file:
    VERSION = version_file.read().strip()

class BuildCommand(build_py):
    def run(self):
        build_py.run(self)
        if not self.dry_run:
            target_dir = os.path.join(self.build_lib, NAME)
            with open(os.path.join(target_dir, "VERSION"), "w") as f:
                f.write(VERSION)
 
setuptools.setup(
    author="Julian Mann",
    author_email="julian@conductortech.com",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python"
    ],
    cmdclass={"build_py": BuildCommand},
    description=DESCRIPTION,
    entry_points={"console_scripts": ["skulk=skulk.skulk:main"]},
    include_package_data=True,
    install_requires=["GitPython>=2.1.15", "twine>=1.15.0"],
    long_description=DESCRIPTION,
    long_description_content_type="text/markdown",
    name=NAME,
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    options={"bdist_wheel": {"universal": True}},
    # python_requires=REQUIRES_PYTHON,
    url="https://github.com/AtomicConductor/skulk",
    version=VERSION,
    zip_safe=False
)
