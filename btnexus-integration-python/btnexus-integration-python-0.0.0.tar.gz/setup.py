from setuptools import setup, find_packages
# import pathlib
import os

# The directory containing this file
# HERE = pathlib.Path(__file__).parent
HERE = os.path.dirname(__file__)

# The text of the README file
readmePath = os.path.join(HERE , "README.md")
README = ""
with open(readmePath) as readmeFile:
    README = readmeFile.read()


if 'VERSION' in os.environ:
    VERSION = os.environ['VERSION']
else:
    VERSION = '0.0.0'

# VERSION = (HERE / "VERSION").read_text()
# try:
#     VERSION += '.{}'.format(os.environ["CI_PIPELINE_IID"])
# except:
#     print('LOCAL BUILD')



setup(name='btnexus-integration-python',
    version=VERSION,
    description="Provides utilities for btNexus Integrations in python",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://btnexus.ai",
    author="Blackout Technologies",
    author_email="dev@blackout.ai",
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages = find_packages(),
    py_modules=['btIntegration'],
    install_requires=[
          'btnexus-node-python~=6.3.233'
    ],
)
