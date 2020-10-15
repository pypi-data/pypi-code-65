import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="neurotpr", 
    version="0.0.3",
    author="Jimin Wang and Yingjie Hu",
    author_email="yhu42@buffalo.edu",
    description="A Neuro-net ToPonym Recognition model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/geoai-lab/NeuroTPR",
    packages=setuptools.find_packages(),
    install_requires=[
          'tensorflow',
          'keras',
          'tensorflow-hub',
          'emoji',
          'nltk'
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)