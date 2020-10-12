import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dysonclient",
    version="0.0.2",
    author="Smore",

    url="https://github.com/smore-inc/dyson-client",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2.7"
    ],
    python_requires='>2.7,<3',
    install_requires=['grpcio', 'grpcio-tools']

)
