import sys
from setuptools import setup

message = 'You tried to install "autodataset", you may look for "autodatasets"'

argv = lambda x: x in sys.argv

if (argv('install') or  # pip install ..
        (argv('--dist-dir') and argv('bdist_egg'))):  # easy_install
    raise Exception(message)

if argv('bdist_wheel'):  # modern pip install
    raise Exception(message)

setup(
    name='autodataset',
    version='0.0.1',
    description=message,
    license='Apache 2.0',
)


