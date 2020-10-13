import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='gsheet-chart',
  version='0.0.2',
  description='Make graph from google sheets',
  long_description = README,
  long_description_content_type = 'text/markdown',
  url='',  
  author='Sunidhi Batra',
  author_email='sunidhibatra08@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='chart', 
  packages=['gsheet-chart'],
  include_package_data = True,
  install_requires=['pandas','gspread','oauth2client','matplotlib'],
)