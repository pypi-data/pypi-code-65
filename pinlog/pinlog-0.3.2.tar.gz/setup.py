import setuptools
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='pinlog',
    version='0.3.2',
    author="Savage Lasa",
    author_email="superoutput@gmail.com",
    description="PinLog is a powerful driver and library integrated several logging systems.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/superoutput/pinlog",
    license='Savage',
    install_requires=[
        'pintrace >= 0.3.2'
    ],
    scripts=['pinlog'],
    keywords='python log driver library integrated integration logging system',
    packages=['pinlog'],
    package_dir={'pinlog':'src/main/pinlog'},
    package_data={},
    include_package_data=True
)