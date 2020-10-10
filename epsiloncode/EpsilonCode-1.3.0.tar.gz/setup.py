import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="EpsilonCode",
    version="1.3.0",
    author="Shreenabh Agrawal",
    author_email="me@shreenabh.com",
    description="Generate and Debug Python code from the Command Line!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://epsilon.shreenabh.com/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=['epsilonCode/epsilon.sh'],
    install_requires=['openai'],
    python_requires='>=3.6',
)
