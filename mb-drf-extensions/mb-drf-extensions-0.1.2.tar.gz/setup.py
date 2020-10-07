#!/usr/bin/env python
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('mb_drf_extensions/__init__.py', 'r') as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

with open('README.md', 'rb') as f:
    readme = f.read().decode('utf-8')

setup(
    name='mb-drf-extensions',
    version=version,
    description='Mind Bricks Django Rest Framework Extensions',
    long_description=readme,
    packages=[
        'mb_drf_extensions',
    ],
    install_requires=[
        'bson>=0.5.0',
        'django>=1.11.0',
        'django-filter>=2.4.0',
        'djangorestframework>=3.7.0',
        # 'drf-extensions>=0.6.0',
        'requests>=2.0.0',
        'requests-mock>=1.8.0',
    ],
    include_package_data=True,
    url='https://www.mind-bricks.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
    ],
)
