import setuptools

with open("README.md", "rt") as fh:
    long_description = fh.read()

setuptools.setup(
    name="randbyrand", 
    version="1.0.0",
    author="Luca Franceschini",
    author_email="luca.france@outlook.com",
    description="Retrive a million random digits by RAND Corporation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lucafrance/randbyrand",
    license="MIT License",
    py_modules=["randbyrand"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=["requests", "numpy", "pandas"]
)