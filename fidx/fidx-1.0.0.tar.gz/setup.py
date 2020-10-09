import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / 'README.md').read_text()

# This call to setup() does all the work
setup(
  name='fidx',
  version='1.0.0',
  description='Float and custom indexes in Python',
  long_description=README,
  long_description_content_type='text/markdown',
  project_urls={
        'Source': 'https://gitlab.com/DPDmancul/fidx',
        'Tracker': 'https://gitlab.com/DPDmancul/fidx/-/issues',
        'Documentation': 'https://gitlab.com/DPDmancul/fidx/-/wikis/home',
    },
  author='Davide Peressoni',
  author_email='dpdmancul+fidx@gmail.com',
  license='MIT',
  classifiers=[
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
  ],
  packages=['fidx'],
  extras_require={
    'NumPy support': ['numpy'],
  }
)
