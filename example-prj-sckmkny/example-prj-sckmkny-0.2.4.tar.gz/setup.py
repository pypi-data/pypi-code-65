import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

install_requires = []
with open('requirements.txt') as f:
    for line in f:
        line, _, _ = line.partition('#')
        line = line.strip()
        install_requires.append(line)

setuptools.setup(
    author="John Tucker",
    author_email="john@larkintuckerllc.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    description="A small example project with single package.",
    install_requires=install_requires,
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="example-prj-sckmkny",
    packages=setuptools.find_packages(),
    python_requires='>=3.8',
    url="https://github.com/larkintuckerllc/example-prj-sckmkny",
    version="0.2.4",
)
