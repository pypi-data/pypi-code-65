import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sudokupy",
    version="0.0.1",
    author="Selcuk Kopru",
    author_email="selcuk.kopru@gmail.com",
    description="Python sudoku generator and solver",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/skopru/pysudoku",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
