from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["DependencyParser/*.pyx"],
                          compiler_directives={'language_level': "3"}),
    name='NlpToolkit-DependencyParser-Cy',
    version='1.0.0',
    packages=['DependencyParser'],
    package_data={'DependencyParser': ['*.pxd', '*.pyx', '*.c', '*.py']},
    url='https://github.com/olcaytaner/TurkishDependencyParser-Cy',
    license='',
    author='olcaytaner',
    author_email='olcaytaner@isikun.edu.tr',
    description='Turkish Dependency Parser',
    install_requires=['NlpToolkit-MorphologicalAnalysis-Cy']
)
