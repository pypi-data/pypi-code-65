import ast
import io
import re

from setuptools import setup, find_packages

with io.open('README.md', 'rt', encoding="utf8") as f:
    readme = f.read()

_description_re = re.compile(r'description\s+=\s+(?P<description>.*)')

with open('lektor_tinymce.py', 'rb') as f:
    description = str(ast.literal_eval(_description_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='lektor-tinymce',

    author='Grigory Vartanyan',
    author_email='gvartanyan@spherical.pm',

    description=description,
    keywords=['lektor', 'plugin', 'tinymce', 'rich-text', 'editor', 'wysiwyg'],
    license='MIT',
    long_description=readme,
    long_description_content_type='text/markdown',

    packages=find_packages(),
    py_modules=['lektor_tinymce'],
    version='0.3',

    classifiers=[
        'Framework :: Lektor',
        'Environment :: Plugins',
    ],

    entry_points={
        'lektor.plugins': [
            'tinymce = lektor_tinymce:TinyMCEPlugin',
        ]
    }
)
