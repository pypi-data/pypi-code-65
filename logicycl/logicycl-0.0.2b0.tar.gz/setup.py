import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="logicycl",
    version="0.0.2b",
    author="StephenKevin",
    author_email="hyuncankun@outlook.com",
    description="Lib for generating logical express",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/StephenKevin/logicycl",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)