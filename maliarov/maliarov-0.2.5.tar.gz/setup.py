import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="maliarov",
    version="0.2.5",
    description="Routine automation",
    packages=['maliarov'],
    py_modules=['common', 'webdriver'],
    include_package_data = True,
    package_data = {
        '': ['*.txt'],
        'maliarov': ['data/*.*'],
    },
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires = [
        "selenium ~= 3.141.0",
        "datetime ~= 4.3",
        "beautifulsoup4 ~= 4.9.0",
        "urllib3 ~= 1.25.9"
    ],
    author="Anatolii Maliarov",
    author_email="tly.mov@gmail.com",
    url="https://github.com/tlmy/webscraping",
)
