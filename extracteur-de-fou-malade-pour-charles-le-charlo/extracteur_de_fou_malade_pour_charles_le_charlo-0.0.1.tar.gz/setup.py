import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

dependencies = dependencies = [
    "textract>=1.6.3",
    "bbcode>=1.0.33",
    "pdfminer3>=2018.12.3.0",
    "ftfy>=5.5.1",
    "langid>=1.1.6",
    "sumy>=0.8.1"
]

setuptools.setup(
    name="extracteur_de_fou_malade_pour_charles_le_charlo",
    version="0.0.1",
    author="Jordan",
    author_email="hehe@example.com",
    description="PDF data parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=dependencies
)