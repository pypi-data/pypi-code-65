import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="printnum",
    version="0.0.6",
    author="alena-lark",
    author_email="AllyLarck@yandex.com",
    description="Printing a number of atoms in a molecule",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alena-lark/PrintNumAtom",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
