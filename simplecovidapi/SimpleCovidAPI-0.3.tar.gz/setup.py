import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='SimpleCovidAPI',
    version='0.3',
    author='GadhaGod',
    author_email='gadhaguy13@gmail.com',
    description='A client library for the SimpleCovidAPI to get covid19 data.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gadhagod/SimpleCovidAPI',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'requests',
    ],
    python_requires='>=3.6'
)
