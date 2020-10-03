from setuptools import find_packages, setup

import numpy as np
from Cython.Build import cythonize


with open("README.md", 'r') as f:
    long_description = f.read()


setup(
    name="classification_library",
    version="0.0.3",
    packages=find_packages(),
    author="Arin Khare",
    description="A classification library using a novel audio-inspired algorithm.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/lol-cubes/classification-library",
    ext_modules=cythonize(["classification_library/__init__.pyx"]),
    include_dirs=np.get_include(),
    install_requires=[
        'numpy>=1.19.2',
        'PyObjC;platform_system=="Darwin"',
        'PyGObject;platform_system=="Linux"',
        'playsound==1.2.2'
    ]
)