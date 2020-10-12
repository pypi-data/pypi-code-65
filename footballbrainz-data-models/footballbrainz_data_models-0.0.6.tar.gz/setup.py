import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="footballbrainz_data_models",
    version="0.0.6",
    description="Data models for footballbrainz",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Casimir Desarmeaux",
    packages=setuptools.find_packages(),
    install_requires=[],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
