import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DialogTag", # Replace with your own username
    version="1.0.0",
    author="Bhavitvya Malik",
    author_email="bhavitvya.malik@gmail.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bhavitvyamalik/DialogTag",
    packages=setuptools.find_packages(),
    install_requires=[
        'transformers>=3.0.0',
        'tqdm',
        'tensorflow>=2.0.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
