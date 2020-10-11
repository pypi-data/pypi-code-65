import os
import setuptools
from setuptools import setup

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="liberation-direct",
    version="1.0.1",
    description="Parse Libération's live news page.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/massoncl/liberation-direct",
    author="Clément Masson",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=["beautifulsoup4", "markdownify"],
    packages=["liberation_direct"],
    include_package_data=True,
)
