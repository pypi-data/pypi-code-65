import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zla_class", # Replace with your own username
    version="1.0.5",
    author="zlakeaw",
    author_email="zla.naratip@gmail.com",
    description="zla_class for get wholesale and retails sale",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires= ['numpy','pandas','pyodbc','datetime','zla_utilities','zla_general',''],
    python_requires='>=3.6',
)