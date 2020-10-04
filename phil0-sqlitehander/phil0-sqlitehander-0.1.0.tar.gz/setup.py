import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='phil0-sqlitehander',
    version='0.1.0',
    author='Philip Fritz',
    author_email='philipjfritz@gmail.com',
    description='A handler for the sqlite3 library for ease of use and setting up a database.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Phil-0/sqlitehandler',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Database',
        'Natural Language :: English'
    ],
    python_requires='>=3.6',
)
