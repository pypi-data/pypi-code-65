from setuptools import find_packages, setup

long_description = "With this package you can easily securely detect the true type of a file. The true type is " \
                   "determined by analyzing the data of the type - not by just looking at the header."

current_version = "0.1.3"

setup(
    name="secure-file-detection",
    packages=find_packages(),
    version=str(current_version),
    license="MIT",
    description="Detect true types of files.",
    long_description=long_description,
    author="Myzel394",
    author_email="myzel394.xyllian@gmail.com",
    url="https://github.com/Myzel394/secure-file-detection",
    download_url="https://github.com/Myzel394/secure-file-detection/archieve/v_" + str(current_version) + ".tar.gz",
    keywords=["detect-file", "mimetype", "detect-mime", "real-type", "file-type", "file", "type"],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
        "openpyxl",
        "svglib",
        "vidhdr",
        "python-docx",
        "python-pptx",
        "chardet",
        "pdfminer.six"
    ]
)