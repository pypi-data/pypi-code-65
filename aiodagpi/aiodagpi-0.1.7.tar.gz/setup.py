import io
import os
import re

from setuptools import find_packages
from setuptools import setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding='utf-8') as fd:
        return re.sub(text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'), fd.read())


setup(
    name="aiodagpi",
    version="0.1.7",
    url="https://github.com/DevilJamJar/aiodagpi",
    license='MIT',

    author="Raj Sharma",
    author_email="yrsharma@icloud.com",

    description="An asynchronous python API wrapper for Dagpi : https://dagpi.tk",
    long_description=read("README.rst"),

    packages=find_packages(exclude=('tests',)),

    install_requires=["aiohttp"],
    extra_requires=["twine", "pytest"],

    keywords=[
        'dagpi',
        'aiodagpi',
        'async',
        'aiohttp',
    ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Framework :: AsyncIO',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
