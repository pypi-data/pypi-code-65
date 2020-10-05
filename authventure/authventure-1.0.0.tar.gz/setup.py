import setuptools

requirements = []
with open("requirements.txt") as file:
    for line in file:
        line = line.strip()
        requirements.append(line)


setuptools.setup(
    name="authventure",
    version="1.0.0",
    author="Jesus Hernando Sancha",
    author_email="jesushs80@gmail.com",
    description="Library for the simpler user authentication",
    packages=setuptools.find_namespace_packages(),
    install_requires=requirements,
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
