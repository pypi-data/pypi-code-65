import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TradingAlgorithm-noahxl10", # Replace with your own username
    version="0.0.2",
    author="Noah Alex",
    author_email="noahxl10@gmail.com",
    description="A package to trade for you!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/noahxl10/trade-algo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    py_modules=["tickerpicker", "trader"],
    python_requires='>=3.1',
    package_data={  # Optional
        'tickerpicker': ['tickers.csv'],
            },
    #package_data={'capitalize': ['data/cap_data.txt']},
    install_requires=['scipy', 'numpy', 'pandas', 'yfinance', 'seaborn', 'datetime', 'iexfinance', 'alpaca_trade_api']
)