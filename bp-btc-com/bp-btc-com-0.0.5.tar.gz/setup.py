import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bp-btc-com",
    version="0.0.5",
    author="Joe Pasquantonio/Qiao Liang",
    author_email="liang.qiao@binance.com",
    description="An api wrapper for btc.com block explorer api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qlbnb/btc-com",
    packages=setuptools.find_packages(),
    python_requires='>=3',
    install_requires=['requests'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
