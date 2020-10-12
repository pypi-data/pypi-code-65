from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = []

setup(
    name="yaml2env",
    version="0.0.1",
    author="Vinay Patil",
    author_email="vinay.hpatil@gmail.com",
    description="A package to convert yaml file to exportable environmental variable",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/patilvinay/yaml2env",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
