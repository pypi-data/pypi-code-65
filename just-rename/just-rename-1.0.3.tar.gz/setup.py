# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# with open('requirements.txt', "r", encoding="utf-8") as f:
#    requires = f.read().splitlines()


setup( 
    name = "just-rename", 
    packages = find_packages(where='.'), 
    version = "1.0.3",

    entry_points = {
        "console_scripts": [
            'just-rename = lhnrenamer.rename:main'
        ]
    },

    description = "just-rename, batch rename filenames, all scripts will be written with Python3",
    author = "lhnonline",
    author_email = "0376lhn@gmail.com",
    license = "GPLv3",
    url = "http://github.com/lhnonline/renamer",
    
    # install_requires = requires,

    include_package_data = True,
    zip_safe=True,
    exclude_package_data = {'': ['__pycache__']},

    # download_url = "",
    keywords = [ "renamer", "batch rename filenames with regex support", "just-rename"],
    classifiers = [ 
        "Programming Language :: Python", 
        "Programming Language :: Python :: 3" ,
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    ],

    long_description = long_description,
    long_description_content_type="text/markdown",
)