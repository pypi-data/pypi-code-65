#!/usr/bin/env python
# coding: utf-8

# In[3]:


from setuptools import setup, find_packages
 
classifiers = [
 
  'Operating System :: OS Independent',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='googlesxtractor',
  version='0.0.1',
  description='google sheets data extractor',
  long_description=open('README.txt').read(),
  url='https://github.com/prasannareddy2999',  
  author='Lakshmi Prasanna Reddy',
  author_email='Prasannareddy3555@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='data extractor', 
  packages=find_packages()
  
)


# In[ ]:




