 
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pySEED",
    version="2.0.0",
    author="Valentin Calzada Ledesma, Juan de Anda Suarez",
    author_email="juan.ds@purisima.tecnm.mx",
    description="pySEED is a python inplementation of symmetric-approximation energy-based estimation of distribution (seed): a continuous optimization algorithm, that was published in IEEE Accsses, with DOI: 10.1109/ACCESS.2019.2948199",
    long_description="pySEED-EDA is a Python implementation of the Symmetric-Approximation Energy-Based Estimation of Distribution (SEED) algorithm: A Continuous Optimization Algorithm , which allows the optimization in continuous space for independent variable functions, based on distribution estimation algorithms, in the Univariate Marginal Distribution scheme [2], the main idea is to make a generational change in each population evolution under the Boltzmann distribution probability function (PDF-B), because PDF-B is a function that has the property that states with less energy are unlikely, so SEED converges in each evolution to a better or equal energy state.",
    long_description_content_type="text/markdown",
    url="https://github.com/LIDT-Lab/pySEED.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5.2',
    install_requires=[
   'numpy>=1.18.2'
   ]
)
