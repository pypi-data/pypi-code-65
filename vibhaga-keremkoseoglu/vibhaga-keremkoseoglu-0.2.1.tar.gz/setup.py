""" vibhaga setup module """
import os
import setuptools
from setuptools import find_packages, setup

setuptools.setup(
    name="vibhaga-keremkoseoglu",
    version="0.2.1",
    author="Kerem Koseoglu",
    author_email="kerem@keremkoseoglu.com",
    description="Vibhaga is a dynamic module loader for Python",
    long_description="A dynamic Python module loader",
    long_description_content_type="text/markdown",
    url="https://github.com/keremkoseoglu/vibhaga",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6.5",
    include_package_data=True
)
