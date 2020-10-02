import setuptools
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='pycachedb',
    version='0.3.2',
    author="Savage Lasa",
    author_email="superoutput@gmail.com",
    description="PyCacheDB is a smallest embedded kay-value caching library.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/superoutput/pycachedb",
    license='Savage',
    install_requires=[
        'ZODB >= 5.6.0',
        'redis >= 3.5.3'
    ],
    scripts=['pycachedb'],
    keywords='python cache caching cached embedded database db',
    packages=['pycachedb'],
    package_dir={'pycachedb':'src/main/pycachedb'},
    package_data={},
    include_package_data=True
)