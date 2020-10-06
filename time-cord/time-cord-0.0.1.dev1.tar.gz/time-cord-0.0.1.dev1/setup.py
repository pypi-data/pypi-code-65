import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="time-cord",
    version="0.0.1.dev1",
    author="Ali Yang",
    author_email="califynic@gmail.com",
    description="A Python library for time management tools for Discord",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/califynic/time-cord",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        'Development Status :: 3 - Alpha'
    ],
    python_requires='>=3.6',
)
