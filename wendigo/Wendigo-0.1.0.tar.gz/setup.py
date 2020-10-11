from glob import glob
from setuptools import find_packages, setup
from pip._internal.req import parse_requirements

if __name__ == "__main__":
    install_requires = [
        str(ir.requirement)
        for ir in parse_requirements("./requirements.txt", session=False)
    ]

    setup(
        name="Wendigo",
        version="0.1.0",
        description="Wendigo is a RPA library for Windows (64 bit).",
        long_description=open("README.md").read(),
        long_description_content_type="text/markdown",
        author="medmsyk",
        author_email="michael.lee.maeda@gmail.com",
        install_requires=install_requires,
        url="https://github.com/medmsyk/wendigopy",
        license="Apache License 2.0",
        packages=find_packages(),
        include_package_data=True
    )