import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="GPyM_TM", 
    version="1.1.1",
    author="Jocelyn Mazarura",
    author_email="<jocelyn.mazarura@up.ac.za>",
    description="The following package enables users to perform text modelling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jrmazarura/GPM",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
