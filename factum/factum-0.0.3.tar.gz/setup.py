import setuptools

def get_long_description():
    with open("README.md", "r") as fh:
        return fh.read()

setuptools.setup(
    name='factum',
    version='0.0.3',
    description='a simple agent-inspired DAG composition and execution framework',
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=['networkx', 'matplotlib'],
    python_requires='>=3.5.2',
    author='Jordan Miller',
    author_email="paradoxlabs@protonmail.com",
    url="https://github.com/lastmeta/factum",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
