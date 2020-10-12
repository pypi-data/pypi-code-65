import os
from setuptools import find_packages, setup


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='rrpproxy',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    description='A python connector for RRP Proxy',
    author='Tech',
    author_email='tech@byte.nl',
    url='https://github.com/ByteInternet/rrpproxy',
    download_url='https://github.com/ByteInternet/rrpproxy/archive/20201009.1.tar.gz',
    python_requires='>=3.4',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
