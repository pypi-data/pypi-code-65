from distutils.core import setup
import os


def get_long_desc():

    if not os.path.isfile('README.rst'):
        return

    with open('README.rst') as f:
        desc = f.read()

    return desc


setup(
    name="filevalidation",
    packages=["validatefile"],
    version="1.0.0",
    description="Module to validate file",
    long_description=get_long_desc(),
    author="Ram Prakash Jayapalan",
    author_email="ramp16888@gmail.com",
    url="https://github.com/ram-jayapalan/file-validation",
    download_url=
    "https://github.com/ram-jayapalan/file-validation/archive/v1.0.0.tar.gz",
    keywords="file validation validate",
    classifiers=[
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License"
    ],
)