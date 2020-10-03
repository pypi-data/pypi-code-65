import setuptools

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name="py-kor",
    version="0.0.4",
    author="Korobov Vladislav",
    author_email="vladankor@gmail.com",
    description="My core library with some utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vladankor/py-kor",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
