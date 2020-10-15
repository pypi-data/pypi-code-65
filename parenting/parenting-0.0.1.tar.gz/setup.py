# load libs
from setuptools import setup
import parenting

# read in README.md
with open("description.md", "r") as fh:
    long_description = fh.read()

# catch the version
current_version = parenting.__version__

# define the setup
setup(name='parenting',
      version=current_version,
      description='parenting the Python way',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/till-io/parenting.git',
      author='Lukas Jan Stroemsdoerfer',
      author_email='ljstroemsdoerfer@gmail.com',
      license='MIT',
      packages=['parenting'],
      zip_safe=False)