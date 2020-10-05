import sys
from os import path
from setuptools import setup, find_packages

if sys.version_info[:2] < (3, 4):
    raise RuntimeError("Python version >= 3.4 required.")

setup(
    name='easyqueue-core',
    version='0.0.1',
    author='Eduardo Bustos',
    url='https://github.com/ebustosm6/easy-queue-core.git',
    description='Easy queue basic model',
    long_description=open(path.join(path.dirname(__file__), 'README.md')).read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='easy queue core',
    packages=find_packages(),
    install_requires=[
        'schema',
        'marshmallow',
        'requests'
        ],
)
