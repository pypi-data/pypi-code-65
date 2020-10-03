import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="boardwatch-models",
    version="0.3.0",
    author="Nathan Alexander Page",
    author_email="nathanalexanderpage@gmail.com",
    description="Model classes for larger Boardwatch product",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nathanalexanderpage/boardwatch_models",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Games/Entertainment",
    ],
    python_requires='>=3.8',
)
