import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="autodirs",
    version="1.0.2",
    author="Pushkar Kadam",
    author_email="pushkarkadam17@outlook.com",
    description="A python project to automatically generate directories and sub-directories",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/pushkarkadam/autodirs",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
