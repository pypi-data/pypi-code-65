import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PySuiteCRM",
    version="2020.10.02",
    author="Russell Juma",
    author_email="RussellJuma@gmail.com",
    description="Python client for SuiteCRM v8 API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RussellJuma/PySuiteCRM",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)