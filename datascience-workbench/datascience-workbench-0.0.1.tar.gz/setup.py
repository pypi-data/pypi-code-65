from setuptools import setup


# read the contents of your README file
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='datascience-workbench',
      version='0.0.1',
      description='Utilities for data science projects',
		long_description=long_description,
    	long_description_content_type="text/markdown",
      packages=['src'],
      author = 'Philipp Schmalen',
      author_email = 'philippschmalen@gmail.com',
      zip_safe=False)
