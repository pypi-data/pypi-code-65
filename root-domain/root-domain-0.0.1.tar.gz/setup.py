import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


name = "root-domain"

setuptools.setup(
    name=name,
    version="0.0.1",
    author="Eloy Perez",
    author_email="zer1t0ps@protonmail.com",
    description="Extract root from domain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    url="https://gitlab.com/Zer1t0/" + name,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "root-domain = root_domain.main:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
