import os, sys
import setuptools

with open("README.md", "r") as _file:
    readme = _file.read()

setuptools.setup(
    name="appchance",
    version="0.2.0",
    author="Appchance Backend Special Forces",
    author_email="backend@appchance.com",
    description="Appchance's toolbelt for wizards and ninjas. May be useful using in dungeons.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/appchance/pychance/",
    packages=setuptools.find_packages(),
    install_requires=["doit", "django", "cookiecutter", "ipython"],
    scripts=["bin/dodo"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django :: 3.0",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 2 - Pre-Alpha",
        "Operating System :: POSIX :: Linux"
    ],
    python_requires='>=3',
)
