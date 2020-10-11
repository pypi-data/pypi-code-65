from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='sunidhi',
  version='0.0.2',
  description='Make charts from google sheets',
  long_description = 'Library',
  url='',  
  author='Sunidhi Batra',
  author_email='sunidhibatra08@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='chart', 
  packages=find_packages(),
  install_requires=['pandas','gspread','oauth2client','matplotlib'] 
)

#long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
