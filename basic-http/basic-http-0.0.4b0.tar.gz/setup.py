import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="basic-http",
    version="v0.0.4-beta",
    author="Romulus-Emanuel Ruja",
    author_email="romulus-emanuel.ruja@tutanota.com",
    description="Python 3 http package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/m3sserschmitt/basic-http.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Natural Language :: English'
    ],
    python_requires='>=3.6',
)
