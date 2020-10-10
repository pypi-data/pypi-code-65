# setup.py

import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="generata",
    version="0.0.2",
    description="Generate sample data",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/praveentn/generata",
    author="Praveen Narayan",
    author_email="sigmoidptn@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["generata"],
    include_package_data=True,
    install_requires=["numpy", "pandas"],
    entry_points={
        "console_scripts": [
            "realpython=reader.__main__:main",
        ]
    },
)