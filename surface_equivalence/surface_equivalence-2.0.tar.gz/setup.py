'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Dec 31, 2018
@author: Niels Lubbes

https://python-packaging.readthedocs.io/en/latest/minimal.html
https://pypi.python.org/pypi?%3Aaction=list_classifiers
'''

from setuptools import setup


def readme():
    with open( 'README.md' ) as f:
        return f.read()


setup( name = 'surface_equivalence',
       version = '2.0',
       description = 'Finding surface equivalences',
       long_description = readme(),
       classifiers = [
           'Development Status :: 3 - Alpha',
           'License :: OSI Approved :: MIT License',
           'Programming Language :: Python :: 2',
           'Programming Language :: Python :: 3',
           'Topic :: Scientific/Engineering :: Mathematics',
           ],
      keywords = 'surface equivalences isomorphisms rational projective',
      url = 'http://github.com/niels-lubbes/surface_equivalence',
      author = 'Niels Lubbes',
      license = 'MIT',
      package_dir = {'':'src'},  # https://stackoverflow.com/questions/30737431/module-found-in-install-mode-but-not-in-develop-mode-using-setuptools
      packages = ['surface_equivalence'],
      test_suite = 'nose.collector',
      tests_require = ['nose'],
      entry_points = {
          'console_scripts': ['run-surface-equivalence=surface_equivalence.__main__:main'],
      },
      include_package_data = True,
      zip_safe = False
      )

