import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DataBaseManager", # Replace with your own username
    version="0.0.2",
    author="Aswanth Vc",
    author_email="no-mail@example.com",
    description="A simple Database manager. You can manage database simply without using SQL or any other query language. The Inputs and outputs are in the form of JSON so you can simply share the data across networks. A simple SQL shell was attached to do more with Your Db.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://techabam.000webhostapp.com/DbManager",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)