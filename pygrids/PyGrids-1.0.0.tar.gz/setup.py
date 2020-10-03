from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()


setup(
    name='PyGrids',
    author='Pixymon',
    version='1.0.0',
    author_email='nlarsen23.student@gmail.com',
    packages=['grids'],
    install_requires=['numpy'],
    description='Spreadsheet-like python objects.',
    long_description=long_description,
    long_description_content_type='text/markdown'
)