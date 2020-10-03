import setuptools

with open ("README.md", "r") as fh:
    long_description = fh.read()
    

setuptools.setup (
    name = "my_package-dv1990",
    version = "1.0.0",
    author = "Divya Viswanathan",
    author_email = "divyaviswanathan.pn@gmail.com",
    description = "A package",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/sample/sampleproject",
    packages = setuptools.find_packages(),
    python_requires='>=3.6',
    )
