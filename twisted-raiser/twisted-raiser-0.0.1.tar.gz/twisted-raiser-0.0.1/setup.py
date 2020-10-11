from setuptools import setup
from Cython.Build import cythonize


setup(ext_modules=cythonize("twisted_raiser/raiser.pyx"))
