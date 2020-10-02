from setuptools import setup

with open("requirements.txt") as f:
    required = f.read().splitlines()

    setup(
        name="traxible",
        version="5",
        url="https://gitlab.com/traxix/traxible",
        packages=["traxible"],
        install_requires=required,
        license="GPLv3",
        author="trax Omar Givernaud",
    )
