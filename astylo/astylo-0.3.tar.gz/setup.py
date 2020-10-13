from setuptools import setup

setup(
    name = 'astylo',
    version = '0.3',
    author = 'D. HU',
    author_email = 'dangning.hu@cea.fr',
    description = 'Python tool kit based on astropy, h5py, etc.',
    license = 'BSD',
    keywords = 'astronomy astrophysics',
    url = 'https://github.com/kxxdhdn/astylo',
    project_urls={
        'IDL': 'https://github.com/kxxdhdn/astylo/tree/master/idlib',
        'SwING': 'https://github.com/kxxdhdn/astylo/tree/master/swing_snippets',
        'Tests': 'https://github.com/kxxdhdn/astylo/tree/master/tests',
    },

    python_requires='>=3.6',
    install_requires = [
        'numpy', 'scipy', 'matplotlib', 
        'astropy', 'reproject', 'h5py', 'tqdm', 
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
    ],
    
    ## Plugins
    entry_points={
        # Installation test with command line
        'console_scripts': [
            'astyloading = astylo:iTest',
        ],
    },

    ## Packages
    packages = ['astylo'],

    ## Package data
    package_data = {
        # include *.txt files in astylo/data
        'astylo': ['dat/*.txt'],
    },
)
