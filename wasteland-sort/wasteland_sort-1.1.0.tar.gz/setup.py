import setuptools
import pathlib


HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setuptools.setup(
    name="wasteland_sort",
    version="1.1.0",
    author="Markian Hromiak",
    author_email="markian.hromiak@yahoo.com",
    description="Fully tested and documented version of the Wasteland sorting algorithm",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/MHromiak/wasteland_sort.git",
    packages=setuptools.find_packages(exclude=("test",)),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8.2',    
)
