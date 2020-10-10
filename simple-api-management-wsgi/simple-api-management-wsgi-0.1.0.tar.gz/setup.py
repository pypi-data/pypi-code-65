import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simple-api-management-wsgi", # Replace with your own username
    version="0.1.0",
    author="Simple API Management",
    author_email="sascha@simpleapimanagement.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://simpleapimanagement.com",
    license='Apache Software License',
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Developers",        
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    keywords="api management middleware metrics rate limits log analysis restful api development debug wsgi flask bottle http",
)