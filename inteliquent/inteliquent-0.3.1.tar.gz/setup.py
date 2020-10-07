import os
import re
import setuptools


ROOT = os.path.dirname(__file__)
VERSION_RE = re.compile(r"""__version__ = ['"]([0-9.]+)['"]""")


with open("README.md", "r") as fh:
    long_description = fh.read()


def get_version():
    init = open(os.path.join(ROOT, "inteliquent", "__init__.py")).read()
    return VERSION_RE.search(init).group(1)


requires = ["requests"]


setuptools.setup(
    name="inteliquent",
    version=get_version(),
    author="Inteliquent",
    author_email="tyler.hunt@inteliquent.com",
    description="Python bindings for Inteliquent, a versiatile telecommunications provider",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requires,
    # url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.5",
)
