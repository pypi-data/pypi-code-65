import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Botlabs.py", # Replace with your own username
    version="1.0.1",
    author="Pjotr",
    author_email="pjotrlspdfr@outlook.com",
    description="A simple API wrapper for discordbotlabs.org",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pjotr07740/botlabs.py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)