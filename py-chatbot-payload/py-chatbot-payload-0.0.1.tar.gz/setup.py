import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py-chatbot-payload",  # Replace with your own username
    version="0.0.1",
    author="Praphan Oranphanlert",
    author_email="e23thr@gmail.com",
    description="A package to create a payload for chatbot platforms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/e23thr/py-chatbot-response",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
