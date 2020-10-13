import io
import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

dependencies = [
    "requests >= 1.0.0",
]


package_root = os.path.abspath(os.path.dirname(__file__))
readme_filename = os.path.join(package_root, "README.md")
with io.open(readme_filename, encoding="utf-8") as readme_file:
    readme = readme_file.read()

setup(
    name='bouncer-insight',
    description='Thin Python library for interacting with Bouncer Insight',
    version='0.0.1',
    url='https://getbouncer.com',
    python_requires=">=3",

    author='Bouncer Inc.',
    author_email='support@getbouncer.com',
    long_description=readme,

    packages=find_packages(),
    install_requires=dependencies,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",

    ]
)
