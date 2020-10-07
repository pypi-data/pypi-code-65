"""
Setup.py for KVRocket
"""

from setuptools import setup
version = "0.0.0-2" #NOTE: please blame pypi for the weird version numbers...

setup(
    name='kvrocket',
    version=version,
    description="KVRocket is a lightweight persistent key value store for Python.",
    url='https://github.com/apexapi/kvrocket',
    author='Dan Sikes',
    author_email='dansikes7@gmail.com',
    keywords='python, portable storage, key value store',

    packages=[
        'kvrocket',
    ],

    install_requires=[
        'munch',
        'dill',
    ],
    
    project_urls={
        'Source': 'https://github.com/apexapi/kvrocket',
    },
)