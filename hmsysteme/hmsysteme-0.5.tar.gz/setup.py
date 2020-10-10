from setuptools import setup
setup(name='hmsysteme',
version='0.5',
description='Connection to HM01',
author='stan',
author_email='stan3@gmx.net',
license='MIT',
url='https://github.com/simbabali/hmsysteme',
download_url = 'https://github.com/simbabali/hmsysteme/archive/v0.2.tar.gz',
packages=['hmsysteme'],
zip_safe=False,
install_requires=[
  'pygame',
],)
