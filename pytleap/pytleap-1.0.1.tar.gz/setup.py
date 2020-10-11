#!/usr/bin/env python3
"""Set up pytleap."""
from pathlib import Path

from setuptools import find_packages, setup

PROJECT_DIR = Path(__file__).parent.resolve()
README_FILE = PROJECT_DIR / "README.md"
LONG_DESCRIPTION = README_FILE.read_text(encoding="utf-8")

VERSION = (PROJECT_DIR / "pytleap" / "VERSION").read_text().strip()

GITHUB_URL = "https://github.com/chemicalstorm/pytleap"
DOWNLOAD_URL = f"{GITHUB_URL}/archive/{VERSION}.zip"

PACKAGES = find_packages(exclude=["tests", "tests.*"])

setup(
    name="pytleap",
    packages=PACKAGES,
    python_requires=">=3.7",
    version=VERSION,
    description="Interface to connect to a TP-Link EAP.",
    long_description=LONG_DESCRIPTION,
    author="chemicalstorm",
    author_email="storm+github@chemicalstorm.org",
    long_description_content_type="text/markdown",
    url=GITHUB_URL,
    include_package_data=True,
    license="MIT",
    keywords="tp-link eap",
    download_url=DOWNLOAD_URL,
    install_requires=["aiohttp"],
)
