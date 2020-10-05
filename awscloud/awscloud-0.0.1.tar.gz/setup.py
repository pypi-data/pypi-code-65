from setuptools import setup

with open('README.md', 'r') as fh:
	long_description = fh.read()

setup(
    name = 'awscloud',
    version = '0.0.1',
    author = 'akashjeez',
    author_email = 'akashit63@gmail.com',
    url = 'https://github.com/akashjeez/awscloud',
    description = 'A Python Package to List AWS Cloud Resources for Different AWS Services!',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    classifiers = [
        'Programming Language :: Python :: 3', 
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires = '>=3.8',
    install_requires = ['boto3'],
    py_modules = ['awscloud'],
    package_dir = {'': 'src'}
)
