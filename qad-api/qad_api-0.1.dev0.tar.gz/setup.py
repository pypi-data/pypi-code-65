# Copyright © 2020 HQS Quantum Simulations GmbH. All Rights Reserved.

from setuptools import setup, find_packages
import os

path = os.path.dirname(os.path.abspath(__file__))

# Read version
__version__ = None
with open(os.path.join(path, 'qad_api/__version__.py')) as file:
    exec(file.read())

# Read readme
readme = None
with open(os.path.join(path, 'README.md'), encoding='utf-8') as file:
    readme = file.read()

# Read license
license = None
with open(os.path.join(path, 'LICENSE'), encoding='utf-8') as file:
    license = file.read()

# Read required packages
install_requires = []
with open(os.path.join(path, 'requirements.txt')) as file:
    install_requires = [r.strip() for r in file.readlines()]


setup(
    name='qad_api',
    version=__version__,
    packages=find_packages(exclude=('doc')),
    license='Apache License, Version 2.0',
    long_description=readme,
    long_description_content_type='text/markdown',
    install_requires=install_requires,
    author='Sebastian Lehmann',
    author_email='sebastian.lehmann@quantumsimulations.de',
    url='https://github.com/HQSquantumsimulations/qad-api/'
)

