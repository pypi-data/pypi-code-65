import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

name = "iplist"

setuptools.setup(
    name=name,
    version="0.0.2",
    author="Eloy Perez",
    author_email="zer1t0ps@protonmail.com",
    description="Expand ip ranges to list of ips",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/Zer1t0/" + name,
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "iplist = iplist.main:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
