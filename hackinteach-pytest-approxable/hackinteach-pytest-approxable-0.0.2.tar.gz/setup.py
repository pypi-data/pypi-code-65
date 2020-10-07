from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="hackinteach-pytest-approxable",
    version="0.0.2",
    author="hackinteach",
    author_email="webmaster@hackinteach.com",
    description="A pytest approxable dict mixin for data class",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hackinteach/pytest-approxable",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)