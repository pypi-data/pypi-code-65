from setuptools import setup

with open('README.md', 'r') as fd:
    long_description = fd.read()

setup(name='cellwars',
      version='0.0.1',
      description='The official Python Bot SDK for https://cellwars.io/',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/mfontanini/cellwars-python',
      author='Matias Fontanini',
      author_email='matias.fontanini@gmail.com',
      license='MIT',
      py_modules=['cellwars'],
      zip_safe=False)
