import setuptools

with open("README.md",'r') as fh:
    long = fh.read()

attrs = {
    "name":"PapTcpg",
    "version":"0.1.0",
    "author" : "RapperXandSheepW",


}

setuptools.setup(**attrs)