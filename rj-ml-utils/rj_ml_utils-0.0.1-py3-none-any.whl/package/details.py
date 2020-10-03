

'''
Module with details on package

from rj_ml_utils.package import details
'''


def readme():
    with open('rj_ml_utils/package/README.md', 'r') as f:
        read_me = f.read()
    return read_me


def dependencies():
    with open('rj_ml_utils/package/requirements.txt', 'r') as f:
        required_dependencies = f.read().splitlines()
    return required_dependencies


# Basic package details
name = 'rj-ml-utils'
version = '0.0.1'
description="Utility package for ML"
long_description=readme()
long_description_content_type="text/markdown"
# Git repo URL
url="https://github.com/raghavajoijode/rj-ml-utils"


# Package author details
author="Raghava Joijode"
author_email="raghava.joijode@gmail.com"


# Package dependencies
classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
python_requires='>=3.6'
INCLUDA_PACK=True
install_requires=dependencies()