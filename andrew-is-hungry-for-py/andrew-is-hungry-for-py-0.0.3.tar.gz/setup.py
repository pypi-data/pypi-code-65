import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="andrew-is-hungry-for-py",
    version="0.0.3",
    author="Andrew Lane",
    author_email="andrew.w.lane@gmail.com",
    description="Learning how to publish to PyPi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AndrewLane/andrew-is-hungry-for-py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
