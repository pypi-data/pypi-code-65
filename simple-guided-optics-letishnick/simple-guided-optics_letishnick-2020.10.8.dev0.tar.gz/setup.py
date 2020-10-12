import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simple-guided-optics_letishnick", # Replace with your own username
    version="2020.10.8dev",
    author="Nick Cheplagin",
    author_email="letishnick@gmail.com",
    description="A package that provides several classic calculation methods for guided optics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=[          
                        'simpleoptics', 
                        'simpleoptics.devices',
                        'simpleoptics.epsilon_data', 
                        'simpleoptics.helpers',
                        'simpleoptics.simulators'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    # py_modules=["waveguide"],
    package_data = {'simpeoptics': ['epsilon_data/*.csv']},
    package_dir={'': 'src'},
)