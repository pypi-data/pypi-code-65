import os, sys
import setuptools

with open("README.md", "r") as _file:
    readme = _file.read()

setuptools.setup(
    name="appchance",
    version="0.1.7",
    author="Appchance Backend Team",
    author_email="backend@appchance.com",
    description="In Appchance we trust",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/appchance/pychance/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.7',
)
