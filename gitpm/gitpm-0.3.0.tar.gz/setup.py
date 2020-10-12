from setuptools import setup

long_description = """
|PyPI - Version| |Downloads| |Code style: black|

Git Project Manager
===================

GitPM is a **secure project-management** commandline utility wrapping around git.

*Currently only on Linux.*

GitPM manages your local projects in the form of **bare git
repositories** by giving them unique hexadecimal ids and stores
maintainace-relevant metadata in the repositories file-structure.

You can define your own standards for your local project management with
git by using gitpm as a **python library**.

`Read more on GitHub <https://github.com/finnmglas/gitPM>`__ or
`Contact Finn <https://www.finnmglas.com/contact>`__

.. |PyPI - Version| image:: https://img.shields.io/pypi/v/gitpm?color=000
   :target: https://pypi.org/project/gitpm/
.. |Downloads| image:: https://img.shields.io/badge/dynamic/json?style=flat&color=000&maxAge=10800&label=downloads&query=%24.total_downloads&url=https%3A%2F%2Fapi.pepy.tech%2Fapi%2Fprojects%2Fgitpm
   :target: https://pepy.tech/project/gitpm
.. |Code style: black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
"""

setup(
    name="gitpm",
    version="0.3.0",
    description="Efficient multi git-repository project management.",
    long_description=long_description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: Software Development :: Version Control",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    keywords="git management repositories manager efficiency",
    url="http://github.com/finnmglas/gitPM",
    author="Finn M Glas",
    author_email="finn@finnmglas.com",
    license="MIT",
    packages=["gitpm"],
    entry_points={
        "console_scripts": ["gitpm=gitpm.command_line:main"],
    },
    include_package_data=True,
    zip_safe=False,
)
