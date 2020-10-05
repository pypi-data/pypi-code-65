# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="nn_torch",
    version="0.0.1",
    keywords=("pip", "pytorch", "neural network", "deep learning"),
    description="neural networks implemented by pytorch",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["torch"]
)
