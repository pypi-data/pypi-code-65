import setuptools  

with open("README.md", "r") as fh:  
    long_description = fh.read()  

setuptools.setup(  
    name="turtletext",  
    version="0.0.7",  
    # author="1ntegrale9",  
    # author_email="1ntegrale9uation@gmail.com",  
    description="A turtle writes text.",  
    long_description=long_description,  
    long_description_content_type="text/markdown",  
    # url="https://github.com/1ntegrale9/echidna",  
    packages=setuptools.find_packages(),  
    classifiers=[  
        "Programming Language :: Python :: 3.7",  
        "License :: OSI Approved :: MIT License",  
        "Operating System :: OS Independent",  
    ],  
    package_dir={"": "src"},
    py_modules=["main", "alphabet"],
    entry_points={
        'console_scripts': [
            'turtletext=main:main',
        ],
    },
)  