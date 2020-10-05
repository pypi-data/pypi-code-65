import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
print(setuptools.find_packages())
setuptools.setup(
    name="devai",
    version="0.0a8",
    author="Dev Sharma",
    license="MIT",
    author_email="dev.sharma@columbia.edu",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/devkosal/devai",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
