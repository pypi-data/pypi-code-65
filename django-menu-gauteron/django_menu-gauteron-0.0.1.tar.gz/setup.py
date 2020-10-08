import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django_menu-gauteron",
    version="0.0.1",
    author="Yann Gauteron",
    author_email="yann@gauteron.xyz",
    description="A simple menu middleware for Django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amigne/django_menu",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.8',
)
