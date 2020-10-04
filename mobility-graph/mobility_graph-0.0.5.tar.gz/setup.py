from setuptools import setup, find_packages

"""
Steps to create a package: 
1. python setup.py sdist bdist_wheel
To install the package locally before uploading to PyPi:
pip install -e .
To upload the package to PyPi:
twine upload dist/*
    - insert username and password and you're good. 
Bonus: 
To check whether there are no warnings with the package you run the following command:
twine check dist/*
if everything is okay you should get:
Checking dist\mobility_graph-0.0.2-py3-none-any.whl: PASSED

Another way of uploading is to use this command:
python setup.py sdist upload
"""

classifiers = [
    #'DEVELOPMENT STATUS :: 2 - PRE-ALPHA',
    'Intended Audience :: Education',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mobility_graph',
    version='0.0.5',
    description='This package has the necessary tools to read, analyze and turn mobility data into a graph object',
    long_description=long_description,
    long_description_content_type='text/markdown',
    package_dir={'mobility_graph': 'mobility_graph'},
    packages=['mobility_graph'],
    url='',
    author='Ayman Mahmoud',
    author_email='aymanh.abdelhamid@gmail.com',
    License='MIT',
    classifiers=classifiers,
    keywords=['gtfs', 'transit','mobility'],
    install_requires=['networkx', 'matplotlib'],
    extras_require = {
        "dev": [
          "pytest>=3.7",
        ],
    }
)
