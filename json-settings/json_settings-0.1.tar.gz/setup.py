from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='json_settings',
    version='0.1',
    author="Riskaware Ltd",
    packages=find_packages(),
    description="JSON Configuration File Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/riskaware-ltd/json-settings",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'numpy',
    ]
)