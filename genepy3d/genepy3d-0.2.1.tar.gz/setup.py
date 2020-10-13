import pathlib
from setuptools import setup, find_namespace_packages

# The text of the README file
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

# Setup configuration
setup(
    name='genepy3d',
    version='0.2.1',
    description=(
      "Python Library for 3D Quantitative Geometry in Computation Microscopy"
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    author='genepy3d-team',
    url='https://gitlab.com/genepy3d/genepy3d',
    license="BSD-3-Clause",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    package_dir={'':'src'},
    packages=find_namespace_packages(where="src"),
    include_package_data=False,
    python_requires=">=3.6",
    install_requires=[
        "scikit-learn",
        "matplotlib",
        "pandas",
        "seaborn",
        "requests",
        "tables",
        "numpy-stl",
        "vtk",
        "pyevtk",
        "pathos",
        "pillow",
        "scikit-image",
        "pynrrd",
        "anytree",
				"trimesh",
        "PyAstronomy"
    ]
)
