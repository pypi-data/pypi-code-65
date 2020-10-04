import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="proto-map",
    version="0.0.0",
    author="ambientnuance",
    author_email="ambientnuance@gmail.com",
    description="(placeholder) Prototype powerup for mapping operators in python.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
