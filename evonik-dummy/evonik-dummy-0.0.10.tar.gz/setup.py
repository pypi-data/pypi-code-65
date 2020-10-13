import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="evonik-dummy",
    version="0.0.10",
    author="Benjamin Schiller",
    author_email="benjamin.schiller@evonik.com",
    description="Generate dummy data, e.g., for testing APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://evodl.visualstudio.com/evonik-dummy",
    #packages=setuptools.find_packages(),
    packages=setuptools.find_namespace_packages(include=['evonik.*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "exrex>=0.10.5",
        "faker>=4.1.1",
        "pytest>=6.0.1"
    ],
)
