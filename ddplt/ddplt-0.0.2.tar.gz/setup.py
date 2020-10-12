from setuptools import setup, find_packages

# read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# read description
with open("README.md", 'r') as fh:
    long_description = fh.read()

setup(name="ddplt",
      version='0.0.2',
      packages=find_packages(),
      install_requires=requirements,

      long_description=long_description,
      long_description_content_type='text/markdown',

      author="Daniel Danis",
      author_email="daniel.gordon.danis@gmail.com",
      url="https://github.com/ielis/ddplt",
      description="A package with code from my ML projects that has a potential of being reusable",
      license='GPLv3',
      keywords="plotting machine learning evaluation metrics",
      test_suite='tests')
