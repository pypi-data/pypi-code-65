from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from os import path

# versioning
import versioneer

here = path.abspath(path.dirname(__file__))

setup(
    name='StrBioInfo',
    version=versioneer.get_version(),

    description='The Structura BioInformatics Library',
    # long_description=read('README.md'),

    # The project's main homepage.
    url='https://github.com/jaumebonet/SBI',

    # Author details
    author='Jaume Bonet',
    author_email='jaume.bonet@gmail.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    python_requires='>=3.6',
    project_urls={
        'Documentation': 'http://jaumebonet.cat/SBI',
        'Source': 'https://github.com/jaumebonet/SBI/',
        'Tracker': 'https://github.com/jaumebonet/SBI/issues',
    },

    platforms='UNIX',
    keywords='development',

    install_requires=['numpy', 'pandas>=0.23,<1.0.0', 'scipy', 'beautifulsoup4', 'libconfig>=0.9',
                      'transforms3d>0.3', 'tqdm', 'requests'],

    packages=find_packages(exclude=['docs', 'demo', 'sphinx-docs']),
    include_package_data=True,
    package_data={
        'SBI': ['data/alphabet.csv.gz']
    },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'sbi.aphabetize=SBI.interface.cli.alphabetize:main',
            'sbi.fetch=SBI.interface.cli.fetch:main',
        ],
    },
    cmdclass=versioneer.get_cmdclass(),
)
