from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["Sampling/*.pyx", "Sampling/*.pxd"],
                          compiler_directives={'language_level': "3"}),
    name='NlpToolkit-Sampling-Cy',
    version='1.0.3',
    packages=['Sampling'],
    package_data={'Sampling': ['*.pxd', '*.pyx', '*.c']},
    url='https://github.com/olcaytaner/Sampling-Cy',
    license='',
    author='olcaytaner',
    author_email='olcaytaner@isikun.edu.tr',
    description='Data sampling library'
)
