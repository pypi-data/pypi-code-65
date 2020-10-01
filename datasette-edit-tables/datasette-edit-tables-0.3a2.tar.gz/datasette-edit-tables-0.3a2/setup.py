from setuptools import setup
import os

VERSION = "0.3a2"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-edit-tables",
    description="datasette-edit-tables is now datasette-edit-schema",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    version=VERSION,
    install_requires=["datasette-edit-schema"],
    classifiers=["Development Status :: 7 - Inactive"],
)
