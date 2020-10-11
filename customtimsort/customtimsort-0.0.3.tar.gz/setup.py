import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="customtimsort",
    version="0.0.3",
    author="lehatr",
    author_email="lehatrutenb@gmail.com",
    description="Timsort sorting algorithm with custom minrun",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lehatrutenb/FastTimSort",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
