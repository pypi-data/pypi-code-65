import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="deep-compare", 
    version="1.0.2",
    author="Lavanya Vijayakrishnan",
    author_email="lavanyavijayakrishnan@gmail.com",
    description="A package to compare variables irrespective of their datatype",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lavanyavijayk/deep-compare",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
