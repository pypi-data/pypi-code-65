import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="darius", 
    version="1.0.0",
    author="Leonidios Megalopoutsis",
    author_email="programertv633@gmail.com",
    description="An easy library to use to host an HTTP or a Websocket server with plenty of functionality",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Greece4ever/darius",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
