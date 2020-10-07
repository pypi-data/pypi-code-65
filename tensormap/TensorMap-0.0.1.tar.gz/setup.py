import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TensorMap",
    version="0.0.1",
    author="social-learning",
    author_email="byfan@wisc.edu",
    description="Data Visualizer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/social-learning/TensorMap",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)