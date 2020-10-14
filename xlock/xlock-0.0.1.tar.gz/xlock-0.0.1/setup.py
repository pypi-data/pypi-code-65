#!/usr/bin/env python

import setuptools

setuptools.setup(
  name = 'xlock',
  version = '0.0.1',
  description = 'A simple x-ops toolkit',
  author = 'acegik',
  license = 'MIT',
  url = 'https://github.com/acegik/xlock',
  download_url = 'https://github.com/acegik/xlock/downloads',
  keywords = ['distributed-locks'],
  classifiers = [],
  install_requires = open("requirements.txt").readlines(),
  python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*",
  package_dir = {'':'src'},
  packages = setuptools.find_packages('src'),
)
