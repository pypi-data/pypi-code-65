import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gildcivility_helpers",
    version="0.1",
    author="Geoffe-Ga",
    author_email="geoffe.gallinger@gmail.com",
    description="Helper modules for the gildcivility reddit bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Geoffe-Ga/gildcivility_helpers.git",
    packages=setuptools.find_packages(),
    download_url="https://github.com/Geoffe-Ga/gildcivility_helpers/archive/v_01.tar.gz",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests",
        "pymongo",
        "praw",
        "twilio",
        "datetime",
    ],
    python_requires='>=3.7',
)
