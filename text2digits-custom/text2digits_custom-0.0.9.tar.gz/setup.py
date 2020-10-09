import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="text2digits_custom",
    version="0.0.9",
    author="Shail Choksi, Manesh Narayan",
    author_email="kmaneshnarayan@gmail.com",
    description="A small library to convert text numbers to digits in a string; customized",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ManeshNarayan/text2digits_custom",
    packages=setuptools.find_packages(),
    keywords="text2numbers words2numbers digits numbers custom",
    project_urls={
        'Source': "https://github.com/careless25/text2digits"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
