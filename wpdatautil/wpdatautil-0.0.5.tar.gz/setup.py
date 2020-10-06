"""Package installation setup."""
from pathlib import Path

from setuptools import find_packages, setup

_DIR = Path(__file__).parent


setup(
    name="wpdatautil",
    author="Data Util",
    author_email="user@users.nomail.github.com",
    version="0.0.5",
    description="Utility functions for data processing",
    keywords="utilities",
    long_description=(_DIR / "README_PyPI.md").read_text().strip(),
    long_description_content_type="text/markdown",
    # url="https://pypi.org/project/wpdatautil/",  # Intentionally not enabled or linked to GitHub!
    packages=find_packages(exclude=["scripts", "tests"]),
    python_requires=">=3.8",
    classifiers=[  # https://pypi.org/classifiers/
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
)
