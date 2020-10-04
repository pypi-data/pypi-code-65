import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gbm_autosplit",
    version="0.0.2",
    author="@not-so-fat",
    description="LightGBM/XGBoost interface which tunes n_estimator by splitting data, then refit with entire data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/not-so-fat/gbm_autosplit",
    packages=setuptools.find_packages(),
    install_requires=[
        "lightgbm>=3.0.0", "xgboost"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
