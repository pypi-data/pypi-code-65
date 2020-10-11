import os

from setuptools import setup

path = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join("README.md")) as file:
    README = file.read()

setup(
    name="matplotobjlib",
    packages=["matplotobjlib"],
    package_dir={"": "src"},
    python_requires=">=3.4",
    version="0.9.0",
    author="Lara Shores",
    author_email="lara.shores@outlook.com",
    url="https://github.com/larashores",
    description="Declarative, objected-oriented interface to matplotlib",
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
    ],
    install_requires=[
        "matplotlib",
        "pycertainties ==1.*, >=1.0.2",
        "sympy",
    ]
)
