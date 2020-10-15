import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bccd",
    version="2.0.1",
    author="Derek Fujimoto",
    author_email="fujimoto@phas.ubc.ca",
    description="BNMR/BNQR Beamspot Image Viewer and Analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dfujim/bccd",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: POSIX :: Linux",
    ],
    install_requires=['numpy>=1.19','matplotlib>=3.2.2','pandas>=1.0.5',
                      'scipy>=1.5.1','scikit-image>=0.17.2','astropy>=3.2.1'],
    package_data={'': ['./images']},
    include_package_data=True,
)
