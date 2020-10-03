from setuptools import setup

with open("README.rst", "r") as f:
    long_description = f.read()

setup(
    name="right-triangle",
    version="0.2.0",
    py_modules=["right_triangle"],
    url="https://github.com/lautnerb/right-triangle",
    license="MIT",
    author="Balazs Lautner",
    author_email="lautner.balazs@gmail.com",
    description="Simple Python package that can be used to do calculations "
                "with right-angled triangles",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    python_requires='~=3.8',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Typing :: Typed",
    ],
)
