from setuptools import setup, find_packages

PACKAGE_NAME = "techynotes"
PACKAGE_VERSION = "1.0.0"

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    author="KOM",
    author_email='komsitsolutions@gmail.com',
    scripts=[],
    packages=find_packages(),
    package_data={'':['**/*', '*']},
    include_package_data=True,
    long_description='this app helps to maintain notes on github',
    description=open('README.txt').read(),
    url="https://github.com/kom3/techynotes.git",
    install_requires=["gcg==0.2.0","GitPython==3.1.1","PyGithub==1.47"]

)
