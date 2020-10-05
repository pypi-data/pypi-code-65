try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

tests_require = ['pytest']

long_description = """
Formulator is a plug-and-play property validator for python objects.
"""

setup(
    name="formulator",
    version="0.0.7",
    author="Trijeet Sethi",
    author_email="trijeets@gmail.com",
    maintainer="Trijeet Sethi",
    maintainer_email="trijeets@gmail.com",
    description="Formulator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/Trijeet/formulator",
    packages=['formulator'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Framework :: Pytest",
    ],
    python_requires='>=3.6',
)
