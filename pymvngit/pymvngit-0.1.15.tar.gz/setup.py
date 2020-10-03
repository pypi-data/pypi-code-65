import pathlib
from setuptools import setup,find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# 
setup(
    name="pymvngit",
    version="0.1.15",
    description="Tool to manage a group of Git/Maven projects.",
    long_description=README,
    long_description_content_type="text/markdown",
    #url="",
    author="Ualter Otoni Pereira",
    author_email="ualter.junior@gmail.com",
    keywords = ['maven','git','tool','java','microservices','lerna'],
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["","pymvngit"],
    include_package_data=True,
    install_requires=[            
        'tinydb','Pygments','clipboard','gitpython'
    ],
    entry_points={
        "console_scripts": [
            "pymvngit=pymvngit.pymvngit:main",
        ]
    },
)