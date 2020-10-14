from os import name

from setuptools import find_packages, setup

from callonce._version import __version__


def read_long_description():
    with open('README.md', 'r') as f:
        long_description = f.read()

    return long_description


setup(
    name='callonce',
    version=__version__,
    author='SunDoge',
    author_email='384813529@qq.com',
    description='make a function callable for once or N times',
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/SunDoge/callonce',
    packages=find_packages(exclude=['tests']),
    install_requires=[],
    python_requires='>=3.6',
)
