import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pythematics",
    version="3.0.0",
    author="Leonidios Megalopoutsis",
    author_email="programertv633@gmail.com",
    description="Math library for Equation solving, polynomial and matrix manipulation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Greece4ever/pythematics",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
