from setuptools import setup 
import os

current_dir = os.path.dirname(__file__)
README=os.path.join(current_dir, 'README.md')

setup( name="sdbit04-pythonc",
description="this give a command pythonc to compile any python module",
long_description=README,
long_description_content_type="text/markdown",
version="1.2.0",
author="swapankumarDas",
url="https://github.com/",
packages=["pythonc"],
entry_points={'console_scripts': [
    'pythonc=pythonc.pythonc:main_method',
]},
license='MIT',
classifiers=[
    'License :: OSI Approved :: MIT License'
]
)
