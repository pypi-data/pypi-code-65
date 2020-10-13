

import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE/"README.md").read_text()

# This call to setup() does all the work
setup(
   name="plotursheet", 
   version="0.0.6", 
   descpription="A Python package to plot data from google sheets",
   long_descpription=README,
   long_descpription_content="text/markdown", 
   URL="https://github.com/fat-a-lity/plotursheet",
   author="Varun Chandran", 
   authoremail="varunjay7@gmail.com",
   license="MIT", 
   classifiers=[ 
        "License :: OSI Approved :: MIT License", 
        "Programming Language :: Python :: 3", 
        "Programming Language :: Python :: 3.7", 
   ], 
   packages=["plotursheet"], 
   includepackagedata=True, 
   installrequires=["gsheets","pandas","numpy","matplotlib"], 
   entrypoints={ 
       "console_scripts":[ 
           "plotursheet=plotursheet.__main__:main", 
       ] 
   }, 
 ) 