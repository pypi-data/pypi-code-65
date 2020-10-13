import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="sbdscommons",
    version="0.0.3",
    author="Olof Nilsson",
    author_email="olof.nilsson@snusbolaget.se",
    description="Packages shared between sb data science projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Snusbolaget/data-science",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True
)
