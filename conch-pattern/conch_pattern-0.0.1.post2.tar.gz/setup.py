from setuptools import find_packages, setup

setup(
    name="conch_pattern",
    version="0.0.1.post2",
    packages=find_packages(),
    install_requires=["click", "numpy", "scipy"],
    extras_require={
        "dev": ["pytest"],
        "examples": ["matplotlib"],
        "docs": ["matplotlib", "sphinx"],
    },
)
