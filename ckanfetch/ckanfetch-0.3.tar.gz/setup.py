from setuptools import setup, find_packages

setup(
    name='ckanfetch',
    version='0.3',
    py_modules=['ckanfetch'],
    author="Florian Woerister",
    author_email="e1126205@student.tuwien.ac.at",
    license="GNU Affero General Public License v3.0",
    url="https://github.com/fwoerister/ckan-dataset-fetcher",
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    namespace_packages=['ckanfetch'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        ckanfetch=ckanfetch.cli:retrieve_dataset
    ''',
)