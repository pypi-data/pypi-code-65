""" __Doc__ File handle class """
from setuptools import find_packages, setup

from XOTweet.__version__ import __version__


def dependencies(imported_file):
    """ __Doc__ Handles dependencies """
    with open(imported_file) as file:
        return file.read().splitlines()


with open("README.md") as file:
    setup(
        name="XOTweet",
        license="GPLv3",
        description="XOTweet is a tweet bot that scraps twitter for keywords and returns all valid tweets",
        long_description=file.read(),
        author="Akhil Reni",
        version=__version__,
        author_email="akhil@wesecureapp.com",
        url="https://strobes.co/",
        packages=find_packages(
            exclude=('tests')),
        package_data={
            'XOTweet': [
                '*.txt',
                '*.json']},
        entry_points={
            'console_scripts': ['xo_tweet = XOTweet.xo_tweet:main']},
        include_package_data=True)
