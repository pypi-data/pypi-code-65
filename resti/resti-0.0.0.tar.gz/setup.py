import os
import sys

from setuptools import setup, find_packages


ROOT = os.path.dirname(__file__)

if sys.version_info < (3, 7, 0):
    sys.exit("Python 3.7.0 is the minimum required version")

about = dict()
with open(os.path.join(ROOT, "src", "resti", "__about__.py")) as f:
    exec(f.read(), about)


with open(os.path.join(ROOT, "README.md")) as f:
    long_description = f.read()


with open(os.path.join(ROOT, "requirements.txt")) as f:
    requirements  = f.readlines()

setup(
    name="resti",
    version=about["__version__"],
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/azriele/resti",
    author="Elior Erez",
    author_email="azriele@post.bgu.ac.il",
    license="GNU",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=requirements,
    tests_require=requirements + ["pytest", "pytest-asyncio"],
    include_package_data=True,
    python_requires=">=3.7.0",
    classifiers=[
            "Development Status :: 2 - Pre-Alpha",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
        ],
)
