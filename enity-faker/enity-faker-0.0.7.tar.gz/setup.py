import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="enity-faker", # Replace with your own username
    version="0.0.7",
    author="Anil Vemula",
    author_email="v-anvemu@microsoft.com",
    description="Generates fakes for different entities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://o365exchange.visualstudio.com/O365%20Sandbox/_git/IPMLExp?path=%2Fsrc%2FPanini2%2FSyntheticDataGenerator&version=GBmaster",
    packages=setuptools.find_packages(),
    install_requires=['spacy', 'faker'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)