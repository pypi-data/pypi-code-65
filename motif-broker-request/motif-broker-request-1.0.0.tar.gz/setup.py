import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="motif-broker-request", # Replace with your own username
    version="1.0.0",
    author="Cécile Hilpert",
    author_email="cecile.hilpert@ibcp.fr",
    description="Package to interrogate motif-broker JS microservice with python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MMSB-MOBI/motif-broker-request",
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['requests']
)