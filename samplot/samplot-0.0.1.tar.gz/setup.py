from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='samplot',
  version='0.0.1',
  description='Method to print the graph by just passing coulumn number',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Samyak Jain',
  author_email='jsamyak100@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='plots', 
  packages=find_packages(),
  install_requires=['matplotlib','pandas','numpy'] 
)