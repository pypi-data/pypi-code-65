import setuptools

with open("README.md", "r") as _file:
    readme = _file.read()

setuptools.setup(
    name="appchance",
    version="0.1.0",
    author="Radosław Przytuła",
    author_email="radoslaw.przytula@appchance.com",
    description="In Appchance we trust",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/appchance/toolbelt/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.7',
)
