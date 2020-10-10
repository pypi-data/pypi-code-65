from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='three60cube',
    version='0.0.8',
    description='A class to project 360x180 images onto a cube',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url='https://github.com/UtrechtUniversity/three60cube',
    author='C.S. Kaandorp',
    author_email='c.s.kaandorp@uu.nl',
    license='MIT',
    packages=['three60cube'],
    python_requires = '>=3.6',
    install_requires = [
        'pillow',
        'numpy',
        'scipy',
        'sklearn',
    ],
    zip_safe=False
)