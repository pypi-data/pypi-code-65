import setuptools
from setuptools import find_packages, setup

with open("README.MD", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SnakeShell",
    version="0.0.0.4b1",
    author="Ofsho",
    description="Shell script commands in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(include=[]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    install_requires=['distro', 'numba']
)