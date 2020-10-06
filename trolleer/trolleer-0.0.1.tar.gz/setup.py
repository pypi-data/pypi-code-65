import setuptools

with open("README.txt", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="trolleer", 
    version="0.0.1",
    author="WebSoft-tech",
    author_email="",
    description="Use import trolleer to import package and pip unistall to uninstall package if you don't like it.",
    long_description_content_type="text/plain",
    long_description=long_description,
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
    ],
    python_requires='>=3.6',
)