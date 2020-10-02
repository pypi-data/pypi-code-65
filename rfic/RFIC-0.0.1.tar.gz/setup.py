import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="RFIC",  # Replace with your own username
    version="0.0.1",
    author="Blaise Albis-Burdige",
    author_email="albisbub@reed.edu",
    description="Reed College Finance and Investment Club (RFIC)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_namespace_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
