import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="Flask-Driver8",
    version="0.0.3",
    description="WebDriver server support for Flask applications",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://dev.azure.com/pumpitup/pumpo-number-five/",
    author="Gerogij Boljuba",
    author_email="georgij.boljuba@pumpitup.cz",
    license="Apache 2.0",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["flask_driver8"],
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
    ],
    entry_points={
        "console_scripts": [
            "driver8=flask_driver8.__main__:main",
        ]
    },
)
