import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="file_traversal",
    version="0.1.2",
    author="Alex Beahm",
    author_email="alexanderbeahm@gmail.com",
    description="Simple injectible rescursive file system processor.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/AlexanderBeahm/file-traverser.git",
    packages=["file_traversal"],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)