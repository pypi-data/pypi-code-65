import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dvpipe",
    version="0.0.3",
    author="Chris Diana",
    author_email="cdiana.media@gmail.com",
    description="A small Python utility that pipes data from function to function in sequencial order.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chrisdiana/dvpipe",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)
