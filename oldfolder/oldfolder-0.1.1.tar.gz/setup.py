import setuptools

with open("README.rst", "r", encoding='utf-8') as fh:
    long_description = fh.read()
setuptools.setup(
    name="oldfolder",
    version="0.1.1",
    author="Jon Boland",
    author_email="jon@codeclear.co.uk",
    description="Spring cleans a file directory by storing away its old subdirectories.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/jonboland/oldfolder",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={"console_scripts": ["oldfolder=oldfolder.oldfolder:main"]},
)