import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mobileprint",
    version="0.0.2",
    author="NYU AI4CE",
    author_email="alexandergao@nyu.edu",
    description="GUI for measuring human performance on mobile construction task",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://pypi.python.org/pypi/mobileprint/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'opencv-python==4.4.0.42',
        'gym==0.17.2',
        'matplotlib==3.3.1',
        'numpy==1.19.1'
        ],
)