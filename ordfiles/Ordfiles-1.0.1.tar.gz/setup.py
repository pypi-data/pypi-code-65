import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="Ordfiles",
    version="1.0.1",
    description="Order files in a directory",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/prakhar33",
    author="Prakhar Rai",
    author_email="prakhar98.rai@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["Ordfiles"],
    include_package_data=True,
    install_requires=["setuptools","pathlib"],
    entry_points={
        "console_scripts": [
            "Ordfiles=Ordfiles.arrange:main",
        ]
    },
) 
