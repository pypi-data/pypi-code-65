import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="akeru-cloud-access",
    version="0.0.1r",
    author="Alexander Colvin",
    author_email="alexander.colvin@hotmail.com",
    description="A django package that supports creation of IAM users/roles"
                "and allowing federated access via django users/groups",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/astrix37/akeru-cloud-access",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'django>=3.0',
        'boto3>=1.14.60',
        'requests>=2.24.0',
        'tox'
    ]
)
