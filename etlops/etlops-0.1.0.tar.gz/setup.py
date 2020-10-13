import setuptools

install_requires = open("requirements.txt").read().strip().split("\n")
dev_requires = open("dev-requirements.txt").read().strip().split("\n")
test_requires = open("test-requirements.txt").read().strip().split("\n")

extras = {"dev": dev_requires + test_requires, "test": test_requires}

extras["all_extras"] = sum(extras.values(), [])

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="etlops",
    version="0.1.0",
    author="Carlos Valderrama Montes",
    author_email="carlosvalde9@gmail.com",
    description="ETL Operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/example-project",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=install_requires,
    extras_require=extras,
)
