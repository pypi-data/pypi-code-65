from setuptools import setup

from colorvote import __version__

with open('README.md', 'r') as fh:
  long_description = fh.read()

setup(
  name='colorvote',
  version=__version__,
  description='A package for the colored coins voting protocol',
  url='http://github.com/Ingimarsson/colorvote',
  author='Brynjar Ingimarsson',
  author_email='brynjar@ingimarsson.is',
  long_description=long_description,
  long_description_content_type='text/markdown',
  license='MIT',
  packages=['colorvote'],
  install_requires=[
    'requests',
  ],
  zip_safe=False,
  python_requires='>=3.6'
)
