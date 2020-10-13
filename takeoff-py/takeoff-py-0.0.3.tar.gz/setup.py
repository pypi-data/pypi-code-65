import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="takeoff-py",
    version="0.0.3",
    author="Marcelo Ribeiro",
    author_email="themarceloribeiro@gmail.com",
    description="A Python toolset to launch full stack, mobile projects",
    long_description="A Python toolset to launch full stack, mobile projects. TakeOff helps you create the backend, frontend and client applications using native iOS/Android",
    long_description_content_type="text/markdown",
    url="https://github.com/themarceloribeiro/takeoff-py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)