from setuptools import setup, find_packages

setup(
    name='ckandf',
    version='0.5',
    py_modules=['ckandf'],
    author="Florian Woerister",
    author_email="e1126205@student.tuwien.ac.at",
    license="MIT",
    url="https://github.com/fwoerister/ckan-dataset-fetcher",
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    namespace_packages=['ckandf'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        ckandf=ckandf.cli:retrieve_dataset
    ''',
)