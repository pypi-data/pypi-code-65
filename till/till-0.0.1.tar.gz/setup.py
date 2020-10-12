# load libs
from setuptools import setup
import till

# read in README.md
with open("description.md", "r") as fh:
    long_description = fh.read()

# catch the version
current_version = till.__version__

# define the setup
setup(name='till',
      version=current_version,
      description='Lightweight ML Deployment',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/till-io/till-python',
      author='Lukas Jan Stroemsdoerfer',
      author_email='ljstroemsdoerfer@gmail.com',
      license='MIT',
      packages=['till'],
      zip_safe=False)