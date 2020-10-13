import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="google-client-helper",
    version="0.0.1",
    author="Ian Jones",
    description="Helpers for the Google Drive and Gmail APIs using a service account",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jonesim/google-client-helper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['google-api-python-client', 'google-auth'],
)