"""
Microsoft Word review tools (comments, markup, etc.) with Python
"""

import pathlib

from setuptools import find_packages, setup

here = pathlib.Path().resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name="docxrev",
    version="0.0.0",
    description=("Microsoft Word review tools (comments, markup, etc.) with Python"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/blakeNaccarato/docxrev",
    author="Blake Naccarato",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=["pywin32", "fire"],
)
