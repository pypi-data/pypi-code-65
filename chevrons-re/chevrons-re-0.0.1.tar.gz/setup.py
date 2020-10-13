import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="chevrons-re",
    version="0.0.1",
    author="Ian Gabaraev",
    author_email="hrattisianees@gmail.com",
    description="Chevrons for quotes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ian-Gabaraev/chevrons",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
