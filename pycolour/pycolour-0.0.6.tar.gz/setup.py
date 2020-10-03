import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycolour", # Replace with your own username
    version="0.0.6",
    author="Daniel Smith",
    author_email="daniel@waiora.com.au",
    description="A simple command line colour tool for python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PythonEuropa/pycolour",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)