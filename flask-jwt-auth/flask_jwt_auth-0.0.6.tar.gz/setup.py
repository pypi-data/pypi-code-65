import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flask_jwt_auth",
    version="0.0.6",
    author="Quaking Aspen",
    author_email="info@quakingaspen.net",
    license='MIT',
    description="This module contains a simple class to implement authentication and authorization in a Flask app using JSON Web Token (JWT)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Quakingaspen-codehub/flask_jwt_auth",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    platform=['Any'],
    python_requires='>=3.6',
)