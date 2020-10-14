from setuptools import find_packages, setup
from Betelgeuse.__version__ import __version__


with open("README.md") as file:
    setup(
        name="strobes-betelgeuse",
        license="GPLv3",
        description="Betelgeuse is a wrapper for Strobes API that helps you integrate scans into your CI/CD easily.",
        long_description=file.read(),
        author="Akhil Reni",
        version=__version__,
        author_email="akhil@wesecureapp.com",
        url="https://strobes.co/",
        python_requires='>=3.6',
        packages=find_packages(
            exclude=('test')),
        package_data={
            'Betelgeuse': [
                '*.txt',
                '*.json']},
        entry_points={
            'console_scripts': ['betelgeuse = Betelgeuse.betelgeuse:main']},
        include_package_data=True)
