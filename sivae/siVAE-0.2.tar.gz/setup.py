#!/usr/bin/env python

from distutils.core import setup
from distutils.extension import Extension
from setuptools import find_packages

import numpy

## Snip from setup.py for tensorflow-forward-ad
try:
  from Cython.Distutils import build_ext
except ImportError:
  use_cython = False
else:
  use_cython = True

cmdclass = {}
ext_modules = []
include_dirs = [numpy.get_include()]

# if use_cython:
#   ext_modules += [
#       Extension(
#           "tensorflow_forward_ad.cbfs", ["tensorflow_forward_ad/cbfs.pyx"],
#           include_dirs=include_dirs),
#   ]
#   cmdclass.update({'build_ext': build_ext})
# else:
#   ext_modules += [
#       Extension(
#           "tensorflow_forward_ad.cbfs", ["tensorflow_forward_ad/cbfs.c"],
#           include_dirs=include_dirs),
#   ]


setup(name='siVAE',
      version='0.2',
      description='scalable and interpretable Variational Autoencoder',
      url='https://github.com/quon-titative-biology/siVAE',
      author=['Yongin Choi', 'Gerald Quon'],
      author_email='yonchoi@ucdavis.edu',
      license='MIT',
      packages=find_packages(),
      install_requires=[
            'pandas',
            'matplotlib',
            'scikit-learn',
            'seaborn',
            'tensorflow==1.15',
            "tensorflow-probability==0.8.0",
            'scipy',
            'scikit-image',
            'scanpy',
            'gseapy'],
      extras_requirements = [],
      cmdclass=cmdclass,
      ext_modules=ext_modules
      )
