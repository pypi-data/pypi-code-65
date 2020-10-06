from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()
    

setup(
    name='chemosanitizer',

    version='0.0.2',

    description='A python script to parallelize basic MolVS functions',
    long_description=long_description,
    long_description_content_type="text/markdown",

    url='https://gitlab.unige.ch/Pierre-Marie.Allard/chemo_sanitizer.git',
    download_url='https://gitlab.unige.ch/Pierre-Marie.Allard/chemo_sanitizer/-/archive/version=\'0.0.1\'/chemo_sanitizer-version=\'0.0.1\'.tar.gz',

    author='Pierre-Marie Allard',
    author_email='pierre-marie.allard@unige.ch',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Chemistry',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.8',
    ],

    keywords=['chemoinformatics', 'MolVS'],

    packages=['chemosanitizer'],

    extras_require={
        'sdf_query': ['rdkit'],
        'sdf_query': ['molvs']
    },
)
