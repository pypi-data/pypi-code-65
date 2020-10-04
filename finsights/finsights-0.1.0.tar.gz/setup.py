import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="finsights",
    version="0.1.0",
    description="Derive investment insights",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/qiujunda/finsights",
    author="Finsights",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Operating System :: MacOS"
    ],
    packages=["finsights"],
    python_requires=">=3.8.5"
)