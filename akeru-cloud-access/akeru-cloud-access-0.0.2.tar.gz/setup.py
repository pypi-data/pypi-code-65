import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="akeru-cloud-access",
    version="0.0.2",
    author="Alexander Colvin",
    author_email="alexander.colvin@hotmail.com",
    description="A Django package that supports creation of IAM users/roles"
                " and allows federated access via Django users/groups",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/astrix37/akeru-cloud-access",
    packages=setuptools.find_packages(),
    package_data={'akeru': [
        'templates/akeru/*.html',
        'static/css/*.css',
        'static/js/*.js',
        'static/img/*.png'
    ]},
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
