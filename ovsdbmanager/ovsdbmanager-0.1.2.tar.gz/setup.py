"""
OvsdbManager setup file
"""

import os
import re

from setuptools import setup, find_packages

with open(os.path.dirname(os.path.abspath(__file__)) + "/README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

version = "unknown"
try:
    version = open(os.path.dirname(os.path.abspath(__file__)) + '/ovsdbmanager/_version.py',
                   "rt").read()
except EnvironmentError:
    pass  # Okay, there is no version file.
else:
    VSRE = r"^__version__\s*=\s*['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, version, re.M)
    if mo:
        version = mo.group(1)
    else:
        raise RuntimeError("unable to find version in ovsdbmanager/_version.py")

setup(
    name="ovsdbmanager",
    version=version,
    author="Ferran Cañellas",
    author_email="ferran.canellas@i2cat.net",
    description="A pure Python3 OVSDB API",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://bitbucket.i2cat.net/projects/RAC/repos/ovsdb-manager",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux"
    ],
    python_requires='>=3.5',
)
