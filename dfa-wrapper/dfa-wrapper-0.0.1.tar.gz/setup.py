import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(name='dfa-wrapper',
      version='0.0.1',
      description='Zerion Dataflow Automation API Wrapper',
      long_description=README,
      long_description_content_type="text/markdown",
      url='https://github.com/jhsu98/dfa-wrapper',
      author='Jonathan Hsu',
      author_email='jhsu@zerionsoftware.com',
      license='MIT',
      python_requires='>=3.0',
      packages=['dfa'],
      install_requires=[
            'pyjwt',
            'requests',
            'pytest'
      ],
      zip_safe=False)