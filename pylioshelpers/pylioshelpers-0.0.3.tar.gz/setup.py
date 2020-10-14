import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pylioshelpers",
    version="0.0.3",
    author="Matt Walters",
    description="Set of helpers for Pylios",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pylios/pylioshelpers",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[],
)