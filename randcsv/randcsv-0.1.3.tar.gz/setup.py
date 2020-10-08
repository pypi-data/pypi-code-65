import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="randcsv",
    version="0.1.3",
    author="James W. Spears",
    author_email="james.w.spears@gmail.com",
    description="Generate random CSVs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scriptloom/randcsv",
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["randcsv=randcsv.cli:cli"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
