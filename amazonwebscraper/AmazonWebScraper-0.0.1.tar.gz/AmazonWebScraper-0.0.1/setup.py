import setuptools

with open("README.md", "r") as fh:
    longdescription = fh.read()

setuptools.setup(
    name="AmazonWebScraper",
    version="0.0.1",
    author="Pradham Kuchipudi",
    author_email="pradhamk@gmail.com",
    description="An amazon webscraper",
    long_description=longdescription,
    long_description_content_type="text/markdown",
    url="https://github.com/PKyahhh/AmazonWebScraper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires = '>=3.6',   
)