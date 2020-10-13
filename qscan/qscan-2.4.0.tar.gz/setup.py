import os,qscan
from setuptools import setup,find_packages
from glob import glob

with open('README.md', 'r') as f:
    longdesc = f.read()

setup(
    name="qscan",
    version=qscan.__version__,
    description="Quasar spectrum scanner and first guess Voigt profile modelling software.",
    long_description=longdesc,
    long_description_content_type='text/markdown',
    author="Vincent Dumont",
    author_email="vincentdumont@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    scripts = glob('bin/*'),
    url="https://astroquasar.gitlab.io/qscan/",
    install_requires=["numpy","matplotlib","scipy","astropy"],
    project_urls={
        "Source Code": "https://gitlab.com/astroquasar/programs/qscan",
    },
)
