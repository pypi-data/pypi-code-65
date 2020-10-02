import setuptools
import os
req = ['numpy']

from setuptools import find_packages
lapackDir = "/usr/lib/lapack"
#if (input(f"Use default lapack location({lapackDir}) [Y]/n?").lower() == 'n'):
#lapackDir = input("Enter Lapack path: ")


if __name__ == "__main__":
    from numpy.distutils.core import Extension
    ext1 = Extension(name = 'rqf',
                 sources = ['./fortran/rqs.f', './fortran/rq0.f', './fortran/rq1.f', './fortran/rqbr.f', './fortran/rqfnb.f','./fortran/crq.f'],
                 library_dirs= [lapackDir],
                 libraries = ["lapack"],
            )

    from numpy.distutils.core import setup
    setup(name = 'quantregpy',
          packages          = find_packages(),
          description       = "Translation of R quantreg for python",
          author            = "David Kaftan",
          author_email      = "kaftand@gmail.com",
          version='0.0.9',
          install_requires = ["patsy", "numpy", "scipy", "pandas", "scikit-learn"],
          ext_modules = [ext1]
          )