import setuptools

with open("README.md", "r", encoding='UTF-8') as f:
    long_description = f.read()
setuptools.setup(
    name="testtest_120",
    version="1.0",
    author="dteer",
    author_email="dteer@qq.com",
    description="Celery-based timing tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dteer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
