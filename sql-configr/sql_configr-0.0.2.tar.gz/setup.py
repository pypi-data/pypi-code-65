import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sql_configr", # Replace with your own username
    version="0.0.2",
    author="Ryan Rickgauer",
    author_email="rrickgauer1@gmail.com",
    description="Quickly create a MySQL credentials json file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rrickgauer/sql_configr",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)