import codecs
import os.path

from setuptools import setup, find_packages


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name='enstadtpfaff-platform-mock-api',
    version=get_version('enstadtpfaff_platform_mock_api/__init__.py'),
    packages=find_packages(exclude=('enstadtpfaff_platform_mock_api_playground',),
                           include=('enstadtpfaff_platform_mock_api', 'enstadtpfaff_platform_mock_api.*',)),
    url='',
    license='',
    author='Platform Development Team',
    author_email='platform-dev@iese.fraunhofer.de',
    description='This is the Python API for the EnStadt:Pfaff Platform Mock',
    install_requires=[
        'paho-mqtt'
    ]
)
