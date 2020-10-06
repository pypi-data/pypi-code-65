import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="crawliexpress",  # Replace with your own username
    version="0.1.4",
    author="ToucanTocard",
    author_email="contact@robin.ninja",
    description="Python3 library to ease Aliexpress crawling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/toucantocard/crawliexpress",
    packages=setuptools.find_packages(include=["crawliexpress"]),
    classifiers=[
        "Development Status :: 4 - Beta",  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "jsonnet",
        "bs4",
        "lxml",
        "sphinx_rtd_theme",
        "sphinx-markdown-builder",
    ],
    setup_requires=[],
    tests_require=[],
    keywords=["aliexpress"],
)
