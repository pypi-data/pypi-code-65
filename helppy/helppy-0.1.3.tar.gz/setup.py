import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="helppy",
    version="0.1.3",
    author="Vahid Vaezian",
    author_email="vahid.vaezian@gmail.com",
    description="Knowledge-Base from GitHub .md files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vvaezian/helppy",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
