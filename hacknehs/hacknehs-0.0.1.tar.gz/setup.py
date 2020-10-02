import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hacknehs", 
    version="0.0.1",
    author="Jeffrey Pan",
    author_email="info@hacknehs.org",
    description="An elegant way to get to hacknehs.org faster!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeffreyzpan/hacknehs",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
