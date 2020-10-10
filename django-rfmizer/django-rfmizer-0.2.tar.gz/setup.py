from setuptools import setup


def get_req():
    with open('requirements.txt', 'r') as file:
        return [line.strip() for line in file.readlines()]


setup(install_requires=get_req())
