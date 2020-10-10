from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["ParseTree/*.pyx", "ParseTree/NodeCondition/*.pyx"],
                          compiler_directives={'language_level': "3"}),
    name='NlpToolkit-ParseTree-Cy',
    version='1.0.0',
    packages=['ParseTree', 'ParseTree.NodeCondition'],
    package_data={'ParseTree': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'ParseTree.NodeCondition': ['*.pxd', '*.pyx', '*.c', '*.py']},
    url='https://github.com/olcaytaner/ParseTree-Py',
    license='',
    author='olcaytaner',
    author_email='olcaytaner@isikun.edu.tr',
    description='Constituency Parse Tree Library',
    install_requires = ['NlpToolkit-Dictionary-Cy']
)
