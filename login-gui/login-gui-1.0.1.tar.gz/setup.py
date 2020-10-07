"""PyPI setup script

Script includes primary Python package along with essential
non-Python files, such as QML, svg and .png resources.

Usage:
    python setup.py sdist
"""

import importlib.machinery
import os
import types

# noinspection PyUnresolvedReferences
from setuptools import setup, find_packages

with open("README.md", "r") as f:
    readme = f.read()

version_file = os.path.abspath("login_gui/version.py")
loader = importlib.machinery.SourceFileLoader('version', version_file)
mod = types.ModuleType(loader.name)
loader.exec_module(mod)
version = getattr(mod, 'version')


def get_all_files(qml_dir, list_of_data):
    """
    function parse all file in folder with suffix
    """
    temp_path = qml_dir.replace("\\", "/")
    temp_path = temp_path.replace("login_gui/", "")
    temp_path = temp_path + '/'
    qml_dir = os.path.abspath(qml_dir)
    for root, _, _ in os.walk(qml_dir):
        for suffix in ("ttf", "qml", "js", "txt", "png", "py", "otf", ".svg"):
            rel_path = os.path.relpath(root, qml_dir)
            rel_path = rel_path.replace("\\", "/")
            list_of_data.append(temp_path + rel_path.strip(".") + "/*." + suffix)
    return list_of_data


# Collect non-python data as package data
package_data = list()
package_data = get_all_files('commonlib', package_data)

# get all requirements
requirements = ['py-singleton']

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Utilities"
]

setup(
    name="login-gui",
    version=version,
    description="Gui with User/Password requesting and save in base64",
    long_description=readme,
    long_description_content_type='text/markdown',
    author="Alexander Sacharov",
    author_email="alexander.sacharov@t-online.de",
    url="https://github.com/sashasoft90/login-gui",
    license="MIT",
    packages=find_packages(),
    zip_safe=False,
    package_data={
        "login-gui": package_data
    },
    classifiers=classifiers,
    install_requires=requirements,
)
