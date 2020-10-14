import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyrameters",
    version="0.0.1",
    author="Jonathan Perry-Houts",
    author_email="jon@than.ph",
    description="Read, edit, and output parameters for scientific software.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jperryhouts/pyrameters",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
