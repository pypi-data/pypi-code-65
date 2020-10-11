from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="reportcard",
    version="0.01",
    author="Jeff Levensailor",
    author_email="jeff@levensailor.com",
    description="Report Card",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/levensailor/reportcard",
    keywords=["reportcard"],
    packages=["reportcard"],
    install_requires=[
        "requests==2.22.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
