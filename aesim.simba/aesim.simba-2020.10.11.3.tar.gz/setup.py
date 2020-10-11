#from distutils.core import setup
from setuptools import setup
    
with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(
    # Application name:
    name="aesim.simba",

    # Version number:
    version="2020.10.11.3",

    # Application author details:
    author="AESIM.tech",
    author_email="contact@aesim.tech",
    
    # Packages
    packages=["aesim.simba"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://simba.io",

    license="By using aesim.simba, you agree to the license agreement available here: https://www.simba.io/static/EULA.pdf",
    
    description="Power Electronics and Motor Drive Simulation",

    long_description=long_description,
    long_description_content_type="text/markdown",

    # Dependent packages (distributions)
    install_requires=[
        "wheel",
        "pythonnet",
    ],
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
)
