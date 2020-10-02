import os
import platform
import sys

import setuptools
from setuptools.command.install import install


here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, "open-analytics", "__version__.py")) as f:
    exec(f.read(), about)

with open("README.md", "r") as fh:
    long_description = fh.read()

def _version():
    return about['__version__']

class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != _version():
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, _version()
            )
            sys.exit(info)

dependencies = [
    'requests>=2.5.0',
    'six>=1.9.0',
]


setuptools.setup(
    name="open-analytics-elliottmurray", # Replace with your own username
    version=_version(),
    author="Elliott Murray",
    author_email="elliottmurray@gmail.com",
    description="Our stats collector for python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elliottmurray/python_sdk",
    install_requires=dependencies,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)
