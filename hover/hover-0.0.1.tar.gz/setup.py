import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hover",
    version="0.0.1",
    author="Ernie Thornhill",
    author_email="pepsimixt@gmail.com",
    description="Hovercraft-like machine learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ErnieThornhill/hover",
    packages=setuptools.find_packages(),
    install_requires=[
        "bokeh>=2.0.1",
        "ivis>=1.7",
        "numba>=0.46.0",
        "numpy>=1.14",
        "scipy>=1.4.1",
        "seaborn",
        "sklearn>=0.21.0",
        "snorkel>=0.9.3",
        "spacy>=2.1.9",
        "torch>=1.4.0",
        "tqdm>=4.0",
        "umap-learn>=0.3.10",
        "wasabi>=0.4",
        "wrappy>=0.4",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
