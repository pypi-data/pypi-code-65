import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

with open('LICENSE.md') as f:
    license = f.read()

setuptools.setup(
    name="touchpoint",
    version="0.0.1",
    author="banthaherder",
    author_email="devops@zappospizza.com",
    description="Touchpoint External API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zappospizza/touchpoint-python",
    packages=setuptools.find_packages(exclude=('tests', 'docs')),
    license=license,
    python_requires='>=3.6',
    
)
