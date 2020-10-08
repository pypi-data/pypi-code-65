'''
Created on 8 окт. 2020 г.

@author: ladmin
'''
from setuptools import setup, find_packages

setup(name='fabula-py',
      version='0.0.2',
      description='Framefork for description infrastructure',
      long_description='Framefork for description infrastructure',
      long_description_content_type="text/markdown",
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
      keywords='fabula2',
      url='https://github.com/djmoto24/fabula.git',
      author='skytrain',
      author_email='no067@mail.ru',
      license='MIT',
      packages=find_packages(),
      #install_requires=[
      #    'fabricio',
      #],
      include_package_data=True,
      zip_safe=False)