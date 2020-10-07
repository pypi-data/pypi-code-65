from setuptools import setup

with open("README_pypi.md", "r") as pd:
    long_description = pd.read()

setup(
    name='PtDa',
    version='0.1.7',
    author='Lucky Pratama',
    author_email='lucky.pratama71@yahoo.com',
    description='Python package for data analytics.',
    url='https://github.com/luckyp71/ptda',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='BSD 2-clause',
    packages=['ptda'],
    install_requires=['pandas',
                      'numpy',
                      'scipy',
                      ],

    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)