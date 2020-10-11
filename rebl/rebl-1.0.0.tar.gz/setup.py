import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rebl", # Replace with your own username
    version="1.0.0",
    author="Marc Brevoort",
    author_email="mrjb@dnd.utwente.nl",
    description="rebl, a Regular Expression Based Linter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kleinebre/rebl",
    packages=setuptools.find_packages(),
    scripts=['rebl'],
    data_files=[('bin/.reblrc', ['.reblrc/config.py', '.reblrc/__init__.py'])],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
