#!/usr/bin/env python
"""Package setup"""

import re
import os
import sys

from setuptools import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, "__init__.py")).read()
    return re.match("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [
        dirpath
        for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, "__init__.py"))
    ]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [
        (dirpath.replace(package + os.sep, "", 1), filenames)
        for dirpath, dirnames, filenames in os.walk(package)
        if not os.path.exists(os.path.join(dirpath, "__init__.py"))
    ]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename) for filename in filenames])
    return {package: filepaths}


version = get_version("restless_dj_utils")


setup(
    name="restless_dj_utils",
    version=version,
    url="http://github.com/AdvancedThreatAnalytics/restless_dj_utils",
    license="MIT",
    description="Restless utils for django API development.",
    author="CriticalStart",
    author_email="simon@criticalstart.com",
    packages=get_packages("restless_dj_utils"),
    package_data=get_package_data("restless_dj_utils"),
    test_suite="restless_dj_utils.runtests.runtests.main",
    install_requires=["restless", "pyjwt", "ua-parser"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
