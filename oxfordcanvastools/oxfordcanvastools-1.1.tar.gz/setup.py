import pathlib
import setuptools

setuptools.setup(
    # Module name (lowercase)
    name='oxfordcanvastools',
    version='1.1',

    # Description
    description='A minimal set of tools for interacting with the Canvas API at Oxford',
    long_description=pathlib.Path('README.md').read_text(),
    long_description_content_type='text/markdown',

    # License name
    license='MIT license',

    # Maintainer information
    maintainer='Fergus Cooper',
    maintainer_email='fergus.cooper@cs.ox.ac.uk',
    url='https://github.com/SABS-R3/oxfordcanvastools',

    # Packages to include
    packages=['oxfordcanvastools'],

    # List of dependencies
    install_requires=[
        'requests'
    ],
    python_requires='>=3.6',
)
