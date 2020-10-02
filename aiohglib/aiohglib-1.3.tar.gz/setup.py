import setuptools

with open("README.md", "rt") as frt:
    long_description = frt.read()

setuptools.setup(
    name="aiohglib",
    version="1.3",
    author="Michal Šiška",
    author_email="michal.515k4@gmail.com",
    url="https://bitbucket.org/515k4/aiohglib/",
    description="Mercurial Python asynchronous library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python",
        "Topic :: Software Development :: Version Control",
    ],
    license="MIT",
    packages=["aiohglib"],
    python_requires=">=3.6",
    install_requires=["pytz"],
)
