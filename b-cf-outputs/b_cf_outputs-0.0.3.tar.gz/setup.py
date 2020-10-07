from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

with open('VERSION') as file:
    VERSION = file.read()
    VERSION = ''.join(VERSION.split())

setup(
    name='b_cf_outputs',
    version=VERSION,
    license='Apache License 2.0',
    packages=find_packages(exclude=[
        # Exclude virtual environment.
        'venv',
        # Exclude test source files.
        'b_cf_outputs_test'
    ]),
    description=(
        'Package that helps to gather AWS CloudFormation outputs.'
    ),
    long_description=README + '\n\n' + HISTORY,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        'boto3>=1.14.0,<2.0.0',
        'pytest>=6.0.2,<7.0.0',
        'pytest-cov>=2.10.1,<3.0.0'
    ],
    author='Laimonas Sutkus',
    author_email='laimonas.sutkus@biomapas.com',
    keywords='AWS CloudFormation Output',
    url='https://github.com/biomapas/B.CfOutputs.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ]
)
