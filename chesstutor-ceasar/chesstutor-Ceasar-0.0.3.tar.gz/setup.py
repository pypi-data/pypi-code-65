import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="chesstutor-Ceasar",
    version="0.0.3",
    author="Ceasar Bautista",
    author_email="cbautista2010@gmail.com",
    description="Play chess on the command line.",
    install_requires=['click', 'python-chess'],
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/Ceasar/chesstutor",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
