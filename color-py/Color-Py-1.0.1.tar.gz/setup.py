from setuptools import setup
from setuptools import find_packages

setup(
    name = "Color-Py",
    version = "1.0.1",
    description = "Color handling library written in Python.",
    long_description = "Color handling library written in Python.",
    url = "https://github.com/IceCruelStuff/Color-Py",
    author = "IceCruelStuff",
    license = "Apache-2.0 License",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries'
    ],
    keywords = 'Color handling library written in Python.',
    packages = find_packages(where='.')
)
