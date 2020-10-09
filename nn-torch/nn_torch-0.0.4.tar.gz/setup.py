# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from nn_torch import __version__


def _get_install_requires():
    with open("requirements.txt") as f:
        lines = f.readlines()
        return list(map(lambda s: s.strip(), lines))


setup(
    name="nn_torch",
    version=__version__,
    keywords=("pip", "pytorch", "neural network", "deep learning"),
    description="neural networks implemented by pytorch",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=_get_install_requires()
)
