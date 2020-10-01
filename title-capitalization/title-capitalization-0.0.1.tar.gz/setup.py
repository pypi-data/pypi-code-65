import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="title-capitalization", 
    version="0.0.1",
    author="Sarah Chen",
    author_email="schen21@andover.edu",
    description="A small example package to impose title capitalization upon a string",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/califynic/title-capitalization",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)