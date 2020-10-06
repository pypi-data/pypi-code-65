"""Package installation setup."""
import distutils.text_file
from pathlib import Path
from typing import List

from setuptools import find_packages, setup

_DIR = Path(__file__).parent


def parse_requirements(filename: str) -> List[str]:
    """Return requirements from requirements file."""
    # Ref: https://stackoverflow.com/a/42033122/
    return distutils.text_file.TextFile(filename=str(_DIR / filename)).readlines()


setup(
    name="wpdatautil",
    author="Data Util",
    author_email="user@users.nomail.github.com",
    version="0.0.2",
    description="Utility functions for data processing",
    keywords="utilities",
    long_description=(_DIR / "README_PyPI.md").read_text().strip(),
    long_description_content_type="text/markdown",
    # url="https://pypi.org/project/wpdatautil/",  # Intentionally not linked to GitHub!
    packages=find_packages(exclude=["scripts", "tests"]),
    install_requires=parse_requirements("requirements/install.txt"),
    python_requires=">=3.8",
    classifiers=[  # https://pypi.org/classifiers/
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
)
