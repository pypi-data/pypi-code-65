import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mlops-local",
    version="1.0.5",
    author="Petter Hultin Gustafsson",
    author_email="petter@mlops.cloud",
    description="Package to test preprocessing and ML scripts locally before pushing to the MLOps platform",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_modules=['mlops_local'],
    install_requires=["Click", "docker"],
    python_requires='>=3.6',
    entry_points={"console_scripts": ["mlops=mlops_local.cli:cli"]},
)
