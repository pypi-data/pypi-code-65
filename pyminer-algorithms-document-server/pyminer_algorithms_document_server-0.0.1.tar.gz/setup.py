import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyminer_algorithms_document_server",
    version="0.0.1",
    author="panhaoyu",
    author_email="panhaoyu.china@outlook.com",
    description="A small documentation server for PyMiner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/py2cn/pyminer-algorithms-document-server",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
