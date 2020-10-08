from setuptools import setup, find_packages
from os import path


# Read the contents of README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Perform setup
setup(
    name="blobhub",
    packages=find_packages(exclude=["tests"]),
    version="0.1.5",
    license="MIT",
    description="BlobHub Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="BlobHub",
    author_email="developers@blobhub.io",
    url="https://blobhub.io/",
    keywords=["blobhub", "data", "onnx", "git", "graph"],
    install_requires=[
        "requests"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
