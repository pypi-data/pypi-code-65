import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

name = "nmapxml"

setuptools.setup(
    name=name,
    version="0.0.1",
    author="Eloy Perez",
    author_email="zer1t0ps@protonmail.com",
    description="Library to parse nmap xml output files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/Zer1t0/" + name,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
)
