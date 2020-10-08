from typing import Any, Dict

import setuptools

version: Dict[str, Any] = {}
exec(open("sym/awslambda/version.py").read(), version)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sym-awslambda",
    version=version["__version__"],
    author="SymOps, Inc.",
    author_email="pypi@symops.io",
    description="Sym AWS Lambda Integration Helpers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/symopsio/sym-awslambda-py",
    packages=setuptools.find_namespace_packages(include=["sym.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
    python_requires=">=3.8",
    install_requires=[
        "boto3>=1.14",
        "protobuf",
        "sym-types",
    ],
)
