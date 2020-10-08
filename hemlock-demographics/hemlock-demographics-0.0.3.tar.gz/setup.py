import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hemlock-demographics",
    version="0.0.3",
    author="Dillon Bowen",
    author_email="dsbowen@wharton.upenn.edu",
    description="Hemlock extension for adding demographics to a hemlock project.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://dsbowen.github.io/hemlock-demographics",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'country-list>=0.2.1',
    ]
)