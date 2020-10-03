import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dynamodb_detech_ai", # Replace with your own username
    version="0.0.11",
    author="Example Author",
    author_email="j.velez2210@gmail.com",
    description="DynamoDB utils",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/detech-ai/Data_Pipelines",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)