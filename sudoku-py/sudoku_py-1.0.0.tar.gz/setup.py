import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sudoku_py",
    version="1.0.0",
    author="Lewis Hammond",
    author_email="lewishammond97@gmail.com",
    description="A Python Sudoku solver and generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Lenwee/sudoku-py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)