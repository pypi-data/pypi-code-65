from setuptools import setup,find_packages

setup(
    name='riskpackage',
    version='0.0.1',
    description='this is a risk package',
    long_description = 'this is risk package long description',
    author = 'Abhay',
    author_email='abhayiitk7@gmail.com',
    packages=['riskpackage','reports_utfunc'],
    # packages=find_packages(),
    # py_modules = ['reports_utility'],
    # package_dir = {'':'riskpackage'},
    install_requires = [],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)