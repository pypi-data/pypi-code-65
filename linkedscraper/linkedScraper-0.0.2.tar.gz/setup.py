import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="linkedScraper",
    version="0.0.2",
    author="Noah Alex",
    author_email="noahxl10@gmail.com",
    description="A package to scrape LinkedIn!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/noahxl10/linkedin-scraper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.1',
    package_data={  # Optional
        'linkedScraper': ['chromedriver'],
            },
    #package_data={'capitalize': ['data/cap_data.txt']},
    install_requires=['pandas', 'parsel', 'selenium']
)