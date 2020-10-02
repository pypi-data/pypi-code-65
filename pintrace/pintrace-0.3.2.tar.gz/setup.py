import setuptools
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='pintrace',
    version='0.3.2',
    author="Savage Lasa",
    author_email="superoutput@gmail.com",
    description="PinTrace is a useful tracing library. With easiest usage, just add decorators like Java annotation then able to log, trace and get latency in anywhere.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/superoutput/pintrace",
    license='Savage',
    install_requires=[
        'pycachedb >= 0.3.2'
    ],
    scripts=['pintrace'],
    keywords='pintrace python trace tracing library annotation add-on decorator wrapper',
    packages=['pintrace'],
    package_dir={'pintrace':'src/main/pintrace'},
    package_data={},
    include_package_data=True
)