from setuptools import setup

long_description = """

This is the Internet of Agents Python module for connecting to the IoA.

"""

setup(
    name="ioa",
    version="0.1.0",
    description="Collaborative resource sharing in a network.",
    long_description=long_description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Developers",
    ],
    keywords="ioa internet resources computation communication network",
    url="https://github.com/internet-of-agents/IoA-Python",
    author="Finn M Glas",
    author_email="finn@finnmglas.com",
    packages=["ioa"],
    entry_points={
        "console_scripts": ["ioa=ioa.command_line:main"],
    },
    include_package_data=True,
    zip_safe=False,
)
