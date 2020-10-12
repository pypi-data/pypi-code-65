#!/usr/bin/env python3
from setuptools import setup


from djangocms_algolia import __version__


setup(
    long_description_content_type='text/markdown',
    name='djangocms-algolia',
    version=__version__,
    author='Victor Yunenko',
    author_email='victor@what.digital',
    long_description=open('README.md').read(),
    
    url='https://gitlab.com/victor.yunenko/djangocms-algolia',
    packages=[
        'djangocms_algolia',
    ],
    include_package_data=True,
    install_requires=[
        'django >= 2.2, < 4',
        'django-cms >= 3.7.2, < 4',
        'algoliasearch-django',
        'aldryn-search',
        'beautifulsoup4',
        'django-standard-form == 1.1.1', # because the latest version 1.1.4 from divio isn't present on pypi.org
    ],
)
