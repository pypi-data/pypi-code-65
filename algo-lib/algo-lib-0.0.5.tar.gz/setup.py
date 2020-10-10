import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="algo-lib", # Replace with your own username
    version="0.0.5",
    author="Austin Serif",
    author_email="austin@sans-serif.io",
    description="A small sample package with two search algorithms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/austinserif/algo-lib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)