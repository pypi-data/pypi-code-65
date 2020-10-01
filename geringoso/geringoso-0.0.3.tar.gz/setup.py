from setuptools import setup

setup(
    name="geringoso",
    version="0.0.3",
    author="John Lenton",
    author_email="jlenton@gmail.com",
    description="tool for geringoso",
    long_description="TBD",
    license="MIT",
    packages=["geringoso"],
    entry_points={
        "console_scripts": ["geringoso = geringoso.__main__:main"],
        },
    python_requires=">=3",
    install_requires=['syltippy'],
)
