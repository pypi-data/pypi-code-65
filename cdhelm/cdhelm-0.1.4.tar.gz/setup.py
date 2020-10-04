import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cdhelm",  # Replace with your own username
    version="0.1.4",
    author="Brian Robertson",
    author_email="brian@fulso.me",
    description="Helm interface in cdk8s",
    keywords='cdk8s helm kubernetes k8s',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fulso-me/cdhelm",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['cdk8s', 'pyyaml'],
)
