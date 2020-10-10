from setuptools import setup
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="include-beer-core",
    version="0.1.2",
    description="Core modules for include-beer eco-system",
    long_description=README,
    # long_description_content_type="text/markdown",
    url="https://github.com/mbhein/include-beer-core",
    author="Matthew Hein",
    author_email="matthew.hein@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["core","core.config","core.utils"],
    include_package_data=True,
    install_requires=["pyyaml"],
)
