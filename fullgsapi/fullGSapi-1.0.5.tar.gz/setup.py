from setuptools import setup, find_packages

with open("README.md") as f:
    readme = f.read()


setup(
    name="fullGSapi",
    version="1.0.5",
    author="ThaumicMekanism",
    author_email="thaumicmekanism@gmail.com",
    long_description=readme,
    long_description_content_type="text/markdown",
    licence="MIT",
    packages=find_packages(include=["fullGSapi.api"]),
    python_requires=">=3.6",
    install_requires=["cryptography", "beautifulsoup4", "py-mini-racer", "requests", "pyyaml"],
)
