from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name=open('PACKAGE').read().strip(),
    version=open('VERSION').read().strip(),
    author='Yann Gauteron',
    author_email='yann@gauteron.xyz',
    packages=find_packages(),
    scripts=[],
    url="https://github.com/amigne/django-adminlte",
    description='An integration of the AdminLTE template for Django',
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    install_requires=['django-menu-gauteron'],
    python_requires='>=3.8',

    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
