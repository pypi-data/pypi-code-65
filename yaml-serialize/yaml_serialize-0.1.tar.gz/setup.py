from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='yaml_serialize',
      version='0.1',
      description='A simple way to store python objects in yaml',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/JakeRoggenbuck/yaml_serialize',
      author='Jake Roggenbuck',
      author_email='jake@jr0.org',
      license='MIT',
      packages=['yaml_serialize'],
      zip_safe=False)
