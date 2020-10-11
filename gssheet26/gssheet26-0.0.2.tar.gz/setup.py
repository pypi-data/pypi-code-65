from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = "gssheet26", # name of our package...
    version = "0.0.2",
    author = "Nikhil Shrivastava",
    author_email = "nikhilshrivastava175@gmail.com",
    description = "This is a python package which helps to read the data from Google Spreadsheets.",
    long_description = long_description,
    long_description_content_type="text/markdown",
    url = "https://github.com/NikhilShrivastava/Greendeck-Assignment",
    license = "MIT",
    packages = find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
    ],
    install_requires = ["gspread", "oauth2client", "pandas", "matplotlib"]
)
