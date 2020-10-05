import codecs
import re

import setuptools

with codecs.open('bitmask_decoder/__init__.py', 'r', 'utf-8') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bitmask-decoder",
    version=version,
    author="Stijn Maas",
    author_email="stijn_maas@live.nl",
    description="Python package to decode day-of-week bitmasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RoelantDL/bitmask-decoder",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)