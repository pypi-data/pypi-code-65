import setuptools
import interpret_text

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="anilv-interpret-text", # Replace with your own username
    version="0.0.1",
    author="Anil Vemula",
    author_email="v-anvemu@microsoft.com",
    description="Generates pickle for Encoder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://o365exchange.visualstudio.com/O365%20Sandbox/_git/IPMLExp?path=%2Fsrc%2FPanini2%2FSyntheticDataGenerator&version=GBmaster",
    packages=setuptools.find_packages(),
    install_requires=["numpy",
    "pandas",
    "pydantic",
    "spacy",
    "ipywidgets",
    "transformers==2.4.1",
    "scipy",
    "scikit-learn",
    "tqdm",
    "cached_property",
    "interpret-community",
    "shap>=0.20.0, <=0.29.3"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)