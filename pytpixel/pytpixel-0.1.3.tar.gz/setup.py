import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytpixel",
    version="0.1.3",
    author="LSOffice",
    author_email="lsoffice.noreply@gmail.com",
    description="A python wrapper for Hypixel's API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LSOffice/Hypixel-API-Package",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)