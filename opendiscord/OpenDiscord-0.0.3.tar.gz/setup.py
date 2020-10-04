import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="OpenDiscord", # Replace with your own username
    version="0.0.3",
    author="Pjotr",
    author_email="pjotrlspdfr@outlook.com",
    description="An API wrapper for common discord bot listing sites.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pjotr07740/OpenDiscord",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)