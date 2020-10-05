import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mathstropy", # Replace with your own username
    version="0.0.1.0",
    author="Richard Hamilton",
    author_email="richard.ha@mathstronauts.ca",
    description="Python library with functions to make learning more efficient",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mathstronauts/mathstropy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
	install_requires=[
          'pgzero',
      ],
    python_requires='>=3.6',
)
