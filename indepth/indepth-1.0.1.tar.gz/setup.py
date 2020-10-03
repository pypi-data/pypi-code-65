import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="indepth",
    version="1.0.1",
    author="Sidharth Macherla",
    author_email="msidharthrasik@gmail.com",
    description="A Natural Language Processing toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SidharthMacherla/indepth",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",        
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",  
        "Topic :: Text Processing :: Linguistic"      
    ],
    python_requires='>=3.6',
)