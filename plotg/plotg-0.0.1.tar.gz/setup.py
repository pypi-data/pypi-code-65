from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='plotg',
  version='0.0.1',
  description='A very basic gsheets ploting library',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Ruchit Sherathiya',
  author_email='ruchitsherathiya007@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='gsheets', 
  packages=find_packages(),
  install_requires=['pickel','os','amtplotlib','pandas','google.auth.transport','google_auth_oauthlib','googleapiclient'] 
)