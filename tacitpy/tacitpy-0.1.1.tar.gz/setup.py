import setuptools

with open("README.md", 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name="tacitpy",
    version="0.1.1",
    author="Samuel Knutsen",
    author_email="samuel@knuten.co",
    description="Tacit programming for Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.sr.ht/~knutsen/tacitpy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.2',
)
