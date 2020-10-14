from setuptools import setup, find_packages

with open("readme.md", 'r') as readme_file:
    long_description = readme_file.read()

setup(
    name = "PhysicsNum",
    version = "0.0.1",
    author = "Andreas Evensen",
    author_email = "Andreas.evensen11@gmail.com",
    description = "Numerical methods provided to solve different methods in university studies",
    long_description = long_description,
    py_module = ["Gaussianfit", "Linearreg"],
    include_package_data = True,
    packages = find_packages(),
    license = "MIT",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License"
    ],    
)
