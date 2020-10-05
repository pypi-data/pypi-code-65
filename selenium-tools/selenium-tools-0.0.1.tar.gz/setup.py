import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="selenium-tools",
    version="0.0.1",
    author="Dillon Bowen",
    author_email="dsbowen@wharton.upenn.edu",
    description="Datetime and range slider tools for Selenium.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://dsbowen.github.io/selenium-tools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['selenium>=3.141.0']
)