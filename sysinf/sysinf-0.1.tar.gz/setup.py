import os
from codecs import open

from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as f:
    long_description = f.read()

setup(
  name = 'sysinf',         
  packages = ['sysinf'],
  version = '0.1',
  license='MIT',
  description = 'A package for viewing system information',
  long_description = long_description,
  long_description_content_type = "text/markdown",
  author = ['Vigneshwar K R'],
  author_email = 'vicky.pcbasic@gmail.com',
  url = 'https://github.com/ToastCoder/sysinf',
  download_url = 'https://github.com/ToastCoder/sysinf/archive/master.zip',
  keywords = ['SYSTEM-INFORMATION'],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)
