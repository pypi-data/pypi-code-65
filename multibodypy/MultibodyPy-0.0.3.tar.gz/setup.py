import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MultibodyPy",  # Replace with your own username
    version="0.0.3",
    author="Michael Tahedl",
    author_email="michael.s.tahedl@gmail.com",
    description="A simple Multibody Dynamics Module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=['numpy', 'scipy']
)
