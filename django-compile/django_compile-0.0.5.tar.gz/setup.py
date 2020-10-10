import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django_compile", # Replace with your own username
    version="0.0.5",
    author="Soham Marik",
    author_email="soham.marik@gmail.com",
    description="A small package to compile .py files django projects to .pyc",
    long_description=long_description,
    long_description_content_type="text/markdown",
    #url="https://github.com/sohamM97/django-compile-package",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "django-compile=django_compile:main",
        ]
    }
)