# -*- coding: utf-8 -*-

# python3 -m pip install --user --upgrade setuptools wheel
# python3 -m pip install --user --upgrade twine

# To build:
# python3 setup.py sdist bdist_wheel

# To publish:
# python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# or
# python3 -m twine upload dist/*
# You will be prompted for a username and password. For the username, use __token__. 
# For the password, use the token value, including the pypi- prefix.

# To install:
# # pip install -i https://test.pypi.org/simple/ Pyphonc --user 
# or
# # pip install Pyphonc --user 


from setuptools import setup, find_packages

readme_file = open("README.md", "rt").read()

setup(
    name="gitkit",
    version="0.1.4",
    author="Peter Ullrich",
    author_email="dotup.software@gmail.com",
    packages=find_packages(exclude=['examples', 'tests', 'scripts']),
    include_package_data=True,
#    scripts=["pyphonc/cli.py"],
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    entry_points={  # Optional
        'console_scripts': [
            'gitkit=gitkit.root:cli',
        ],
    },
    url="https://github.com/dotupNET",
    license="GNU General Public License v3.0",
    keywords="dotup git github sync",
    description="Keep your git repositories up to date",
    long_description=readme_file,
    long_description_content_type="text/markdown",
    classifiers=(
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities",
    ),
    python_requires='>=3',
    install_requires=['Click'],
)
