import setuptools  

with open("README.md", "r") as fh:  
    long_description = fh.read()  

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(  
    name="asyncpgw",  
    version="0.0.1",  
    author="furimu",  
    description="asyncpg wrapper",  
    long_description=long_description,  
    long_description_content_type="text/markdown",
    install_requires=requirements,
    url="https://github.com/furimu1234/asyncpgw/tree/main/asyncpgw",  
    packages=setuptools.find_packages(),  
    classifiers=[  
        "Programming Language :: Python :: 3.8",  
        "License :: OSI Approved :: MIT License",  
        "Operating System :: OS Independent",  
    ],  
)  