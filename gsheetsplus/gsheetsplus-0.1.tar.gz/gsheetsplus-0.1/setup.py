import pathlib
from setuptools import setup, find_packages
# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="gsheetsplus",
    version="0.1",
    description="Extend gsheets for added functionalities",
    long_description=README,
    long_description_content_type="text/markdown",
    url="",
    author="Tanmay Pandey",
    author_email="tanmaypandey1998@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["gsheets", "matplotlib"]
)