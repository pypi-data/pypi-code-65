# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


def get_install_requires():
    with open("requirements.txt") as f:
        lines = f.readlines()
        lines.remove('pytest\n')
        return list(map(lambda s: s.strip(), lines))


setup(
    name="nn_torch",
    version="0.0.3",
    keywords=("pip", "pytorch", "neural network", "deep learning"),
    description="neural networks implemented by pytorch",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=get_install_requires()
)
