import setuptools
import re


with open("README.md", "r") as fh:
    long_description = fh.read()

# prepend all relative links with
# https://git.friedl.net/incubator/bytetrie/raw/branch/master/
# to make them absolute
long_description = re.sub("\[(.*)\]\((?!http)(.*)\)", r"[\1](https://git.friedl.net/incubator/bytetrie/raw/branch/master/\2)", long_description)

setuptools.setup(
    name="bytetrie",
    version="0.1.0",
    url="https://git.friedl.net/incubator/bytetrie",
    license="MIT",
    author="Armin Friedl",
    author_email="dev@friedl.net",

    description="A self-compressing, dependency-free radix trie",
    long_description=long_description,
    long_description_content_type="text/markdown",

    packages=setuptools.find_packages(exclude=("tests",)),
    include_package_data=True,

    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ]
)
