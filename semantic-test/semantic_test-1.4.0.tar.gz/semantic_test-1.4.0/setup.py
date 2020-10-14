import re
from setuptools import find_packages, setup
import sys

with open("semantic_test/__init__.py", "r") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

setup(
    name="semantic_test",
    version=version,
    url="http://github.com/mathieuboudreau/semantic_test",
    description="Test python project",
    license="MIT",
    install_requires=[
        "twine>=3,<4",
        "requests>=2.21,<3",
        "wheel",
        "toml~=0.10.0",
    ],


    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
    ],
)
