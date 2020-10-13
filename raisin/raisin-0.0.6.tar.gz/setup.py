import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="raisin",
    version="0.0.6",
    author="Robin RICHARD (robinechuca)",
    author_email="raisin@ecomail.fr",
    description="Cluster Work",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://framagit.org/robinechuca/raisin",
    # packages=setuptools.find_packages(), # devrai fonctionner mais ne trouve pas raisin.worker.shortcut
    packages=["raisin", "raisin.geometry", "raisin.worker", "raisin.communication", "raisin.reader", "raisin.worker.scripts"],
    install_requires=["pycryptodome"], # ces paquets serons installes d'office
    extras_require = {
        "calculation": ["sympy", "giacpy", "numpy"],
        "tools": ["psutil>=5.1", "regex", "cloudpickle"],
        "graphical": ["tkinter", "matplotlib"],
        "security": ["pycryptodome"]
        },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
