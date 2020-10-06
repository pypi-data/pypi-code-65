from setuptools import setup, find_packages

def parse_requirements(requirement_file):
    with open(requirement_file) as f:
        return f.readlines()

setup(
    name='swimlane-faker',
    version='0.0.2',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='A Python package to generate fake data from provided input strings for use with Swimlane',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=parse_requirements('./requirements.txt'),
    keywords=['swimlane'],
    url='https://github.com/swimlane/swimlane-faker',
    author='Swimlane',
    author_email='info@swimlane.com',
    python_requires='>=3.6, !=3.0.*, !=3.1.*, !=3.2.*, <4'
)