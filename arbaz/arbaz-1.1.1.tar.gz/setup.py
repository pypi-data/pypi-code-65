from setuptools import setup
from setuptools import find_packages
 

setup(
name='arbaz',
version='1.1.1',
description='Analysis between Sales vs Time by accessing google sheet from google drive',
long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),  
author='Arbaz Khan',
url='https://github.com/ArbazKhan7/Greendeck-Task2',
author_email='arbazkhanak7777@gmail.com',
license='MIT', 
classifiers = [
'Development Status :: 5 - Production/Stable',
'Intended Audience :: Education',
'Operating System :: Microsoft :: Windows :: Windows 10',
'License :: OSI Approved :: MIT License',
'Programming Language :: Python :: 3.8'
],
keywords='', 
packages=find_packages(),
install_requires=[''] ,
include_package_data=True,

)