"""
Tiny script that prints the idl_version so it can be handed off to Jenkins
"""
from setuptools_scm import get_version

version = get_version()
print(version)