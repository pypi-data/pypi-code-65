import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="constants-and-utils",
    version="0.0.5",
    author="Terminus",
    author_email="jose.salas@zinobe.com",
    description="Constants and utils",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/terminus-zinobe/constants-and-utils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[],
    extras_require={
        "mongoengine": [
            "mongoengine>=0.18.2",
            "Cerberus>=1.3.2",
            "pymongo>=3.10.1",
            "deepdiff>=4.3.2",
            "mongomock==3.20.0"
        ]
    }
)
