from setuptools import setup
from setuptools import find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

packages = find_packages()

setup(
    name="oaas_grpc_compiler",
    version="1.0.1",
    description="oaas_grpc_compiler",
    long_description=readme,
    author="Bogdan Mustiata",
    author_email="bogdan.mustiata@gmail.com",
    license="BSD",
    entry_points={
        "console_scripts": ["oaas-grpc-compiler = oaas_grpc_compiler.mainapp:main"]
    },
    install_requires=[
        "protobuf==3.13.0",
        "grpcio==1.31.0",
        "termcolor_util",
        "black",
    ],
    packages=packages,
    package_data={
        "": ["*.txt", "*.rst"],
        "oaas_grpc_compiler": ["py.typed"],
    },
)
