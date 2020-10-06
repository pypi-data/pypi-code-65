import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="extPep_identifier-blackjack", # Replace with your own username
    version="0.0.8",
    author="Xinhao Shao",
    author_email="",
    description="Extended peptides identification given mass-spec search result and custom proteomic database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://git.pepchem.org/gaolab/api_ribo_ext ",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)