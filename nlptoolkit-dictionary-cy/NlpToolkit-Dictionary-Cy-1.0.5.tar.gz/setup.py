from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["Dictionary/*.pyx", "Dictionary/Trie/*.pyx", "Language/*.pyx", "Syllibification/*.pyx"],
                          compiler_directives={'language_level': "3"}),
    name='NlpToolkit-Dictionary-Cy',
    version='1.0.5',
    packages=['Language', 'Dictionary', 'Dictionary.Trie', 'Syllibification'],
    package_data={'Language': ['*.pxd', '*.pyx', '*.c'],
                  'Dictionary': ['*.pxd', '*.pyx', '*.c', '*.py'],
                  'Dictionary.Trie': ['*.pxd', '*.pyx', '*.c'],
                  'Syllibification': ['*.pxd', '*.pyx', '*.c']},
    url='https://github.com/olcaytaner/Dictionary-Cy',
    license='',
    author='olcaytaner',
    author_email='olcaytaner@isikun.edu.tr',
    description='Simple Dictionary Processing',
    install_requires=['NlpToolkit-Math-Cy']
)
