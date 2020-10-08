from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='fastdev',
      version='0.0.1',
      license='MIT',
      description='tools for fast development of deep learning researchs',
      packages=['fastdev'],
      author='Sihan Wang',
      author_email='jasper.wang530@gmail.com',
      long_description=long_description,
      long_description_content_type='text/markdown',
      download_url='https://github.com/Jasper530/fastdev/archive/0.0.1.tar.gz',
      install_requires=[
          'numpy',
          'matplotlib',
          'torch',
          'transformers'
      ],
      zip_safe=False)