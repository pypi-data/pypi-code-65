import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymultigo", # Replace with your own username
    version="0.0.1",
    author="JiangGua",
    author_email="pymultigo@mg.jonbgua.com",
    description="A MongoDB client to use multiple Mongo databases (MongoDB Atlas)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JiangGua/pymultigo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['pymongo'],
    python_requires='>=3.6',
)