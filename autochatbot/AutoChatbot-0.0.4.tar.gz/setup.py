import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AutoChatbot", # Replace with your own username
    version="0.0.4",
    author="Kritik Seth",
    author_email="sethkritik@gmail.com",
    description="Package that makes chatbots automatically",
    py_modules=['chat'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kritikseth",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
