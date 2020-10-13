import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sample-varun-95",
    version="0.0.1",
    author="varun_95",
    author_email="varunjay7@gmail.com",
    description="A small example package",
    long_description="NOpe",
    long_description_content_type="text/markdown",
    url="https://github.com/fat-a-lity/plotursheet",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)