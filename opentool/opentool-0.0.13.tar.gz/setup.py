import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="opentool",
    version="0.0.13",
    author="huutrinh",
    author_email="trinhsp89@gmail.com",
    description="Tools for AI project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/huutrinh68/opentool",
    packages=setuptools.find_packages(),
    install_requires=[
        'torch>=1.6.0',
        'torchvision>=0.7.0',
        'numpy>=1.19.1',
        'tensorboardX>=2.1',
        'easydict>=1.9',
        'addict>=2.2.1',
        'yapf>=0.30.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
