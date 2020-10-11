import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name='whv',
    version='0.0.1',
    description='Verify webhooks for various providers',
    long_description=README,
    long_description_content_type="text/markdown",
    author='Tom Mitchell',
    url='https://github.com/tmhmitchell/whv',
    classifiers=[
        'Programming Language :: Python :: 3.8',
    ],
    packages=['whv'],
    install_requires=['cryptography', 'requests']
)
