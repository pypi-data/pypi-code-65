import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="compare_date_range",
    version="0.0.1",
    author="Matt Walsh",
    author_email="git@mattwalsh.dev",
    license='MIT',
    description="Compare two date ranges to return overlap information",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="date datetime time range compare overlap",
    url="https://github.com/mattwalshdev/compare_date_range",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
    ],
    install_requires=[
        'datetime',
    ],
    python_requires='>=3.6',
)