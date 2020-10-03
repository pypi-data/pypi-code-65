import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kmon", 
    version="0.1.6",
    author="sjj&jmj",
    author_email="sjj@twinlab.co.kr",
    description="Korea University Monitoring System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/twinlab/korea-monitoring-system",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
