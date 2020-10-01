import os, sys
import setuptools
from setuptools.command.install import install as _install


def _post_install(dir):
    from subprocess import call
    call([sys.executable, 'setup-after.py'],
         cwd=os.path.join(dir, 'appchance'))


class install(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, (self.install_lib,),
                     msg="Running post install task")

with open("README.md", "r") as _file:
    readme = _file.read()

setuptools.setup(
    name="appchance",
    version="0.1.2",
    author="Radosław Przytuła",
    author_email="radoslaw.przytula@appchance.com",
    description="In Appchance we trust",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/appchance/pychance/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.7',
)

