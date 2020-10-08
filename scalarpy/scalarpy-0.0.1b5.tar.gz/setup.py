import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scalarpy", # Replace with your own username
    version="v0.0.1b5",
    author="G D Abhishek",
    author_email="gdabhishek1@gmail.com",
    description="Welcome to ScalarPy!",
    long_description=long_description,
    install_requires=[
   'pandas',
   'numpy','matplotlib','scipy','scikit-learn','imblearn','xgboost','lightgbm','ipywidgets','yellowbrick'],
    long_description_content_type="text/markdown",
    url="https://github.com/ScalarPy/scalarpy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.1',
)