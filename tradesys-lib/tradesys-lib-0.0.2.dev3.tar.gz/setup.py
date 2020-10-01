import setuptools

import codecs
import os.path


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tradesys-lib",
    version=get_version("tradesys/lib/__init__.py"),
    author="Moises Benzan",
    author_email="info@mbenzan.com",
    description="A unified, extensible lib for developing trading algorithms.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="trading forex stocks lib",
    license="GNU",
    url="https://github.com/moisesbenzan/tradesys-sdk",
    project_urls={
        'Documentation': 'https://tradesys.gitlab.io/tradesys-sdk/',
        'Source': 'https://github.com/moisesbenzan/tradesys-sdk',
    },
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",

    ],
    python_requires='>=3.5',
)
