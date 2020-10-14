import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="BO4E",
    version="0.0.1",
    author="Hochfrequenz Unternehmensberatung GmbH",
    author_email="kevin.krechan@hochfrequenz.de",
    description="BO4E implementation for Python3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Hochfrequenz/BO4E-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
