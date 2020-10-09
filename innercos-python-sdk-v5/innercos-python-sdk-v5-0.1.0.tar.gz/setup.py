from setuptools import setup, find_packages
from platform import python_version_tuple


def requirements():

    with open('requirements.txt', 'r') as fileobj:
        requirements = [line.strip() for line in fileobj]
        return requirements


def long_description():
    with open('README.rst', 'r') as fileobj:
        return fileobj.read()


setup(
    name='innercos-python-sdk-v5',
    version='0.1.0',
    url='https://www.qcloud.com/',
    license='MIT',
    author='maysonshen, tiedu, lewzylu, channingliu',
    author_email='dutie123@qq.com',
    description='innercos-python-sdk-v5',
    long_description=long_description(),
    packages=find_packages(),
    install_requires=requirements()
)
