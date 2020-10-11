import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='bdtk',                            # This is the name of your PyPI-package.
    version='0.1.1',                        # Update the version number for new releases
    author='Aurum Kathuria',
    author_email='armkatspamblocker@gmail.com',
    description="A small data analysis package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/aurumkathuria/BDToolkit',
    packages=setuptools.find_packages(),
    install_requires=['pandas>=0.25.1',
                      'numpy>=1.16.5', 
                      'seaborn>=0.9.0',
                      'matplotlib>=3.1.1',
                      'ipywidgets>=7.5.1'
                     ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',    
)