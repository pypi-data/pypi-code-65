import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="asfpy-aridyckovsky",
    version="0.2.1",
    author="Ari Dyckovsky",
    author_email="aridyckovsky@gmail.com",
    description="A collection of Python scripts for the Application Statement Feedback Program's logistics needs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aridyckovsky/asfpy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6"
)
