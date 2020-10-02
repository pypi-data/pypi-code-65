##############################
# BUILDING PYTHON PACKAGE PYPi
##############################
# python3 -m pip install --user --upgrade setuptools wheel
# python3 setup.py sdist
# python3 -m pip install --user --upgrade twine
#  /usr/local/bin/twine check dist/*
#  /usr/local/bin/twine upload dist/*
##############################
import os
import io
import sys
import importlib
from setuptools import find_packages

try:
    importlib.util.find_spec("numpy")
except ImportError:
    import subprocess

    subprocess.call([sys.executable, "-m", "pip", "install", "numpy"])

from numpy.distutils.core import setup, Extension

try:
    from distutils.command import bdist_conda
except ImportError:
    pass

# in development set version to none and ...
PYPI_VERSION = "0.1.18"

# Place install_requires into the text file "requirements.txt"
with open("requirements.txt") as f2:
    requirements = f2.read().strip().splitlines()

# install_requires = open("requirements.txt").read().strip().split("\n")

# install_requires = [
#     "numpy==1.19.2",
#     "scipy==1.5.2",
#     "Cython==0.29.21",
#     "mpi4py==3.0.3",
#     "petsc4py==3.13.0",
#     "h5py==2.10.0",
#     "pandas==1.1.2",
#     "ruamel.yaml==0.16.12",
#     "fastfunc==0.2.3",
#     "meshio==4.2.2",
#     "meshplex==0.13.3",
#     "pre-commit==2.7.1",
#     "vtk==9.0.0",
#     "numpy-indexed==0.3.5",
#     "scikit-fuzzy==0.4.2",
# ]


packs = find_packages(include=["gospl", "gospl.*"])


def git_version():
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ["SYSTEMROOT", "PATH"]:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env["LANGUAGE"] = "C"
        env["LANG"] = "C"
        env["LC_ALL"] = "C"
        out = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd(["git", "rev-parse", "--short", "HEAD"])
        GIT_REVISION = out.strip().decode("ascii")
    except OSError:
        GIT_REVISION = "Unknown"

    return GIT_REVISION


if PYPI_VERSION is None:
    PYPI_VERSION = git_version()


ext = Extension(
    name="gospl._fortran", sources=["fortran/functions.pyf", "fortran/functions.F90"]
)


this_directory = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


if __name__ == "__main__":
    setup(
        name="gospl",
        author="Tristan Salles",
        author_email="tristan.salles@sydney.edu.au",
        url="https://github.com/Geodels/gospl",
        version=PYPI_VERSION,
        license="GPLv3",
        description="A Python interface to perform Global Landscape Evolution Model",
        keywords=[
            "python",
            "paleogeography",
            "sediment-transport",
            "paleoclimate",
            "model",
            "landscape",
            "landscape-evolution",
            "basin-modeling",
            "erosion-process",
            "compaction",
            "lithology",
            "science",
        ],
        long_description=long_description,
        long_description_content_type="text/markdown",
        ext_modules=[ext],
        # packages=["gospl", "gospl.tools", "gospl.flow", "gospl.mesher", "gospl.sed"],
        packages=packs,
        install_requires=requirements,
        setup_requires=[
            [p for p in requirements if p.startswith("numpy")][0],
        ],
        python_requires=">=3",
        classifiers=[
            "Intended Audience :: Science/Research",
            "Programming Language :: Fortran",
            "Operating System :: Unix",
            "Operating System :: MacOS",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
        ],
    )
