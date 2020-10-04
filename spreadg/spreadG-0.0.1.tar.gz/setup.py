import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spreadG", # Replace with your own username
    version="0.0.1",
    author="Himanshu Pal",
    author_email="palhimanshu997@gmail.com",
    description="Plot data from Google sheets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ansh997/SpreadG",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)