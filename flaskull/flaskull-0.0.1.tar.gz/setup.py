from setuptools import setup, find_packages
from flaskull import __version__

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='flaskull',
    version=__version__,
    description='A set of useful class, functions, mixins and snippets to '
                'works with Flask.',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/akonieczny/flaskull',
    author='Adam Konieczny',
    packages=find_packages(include=['flaskull', 'flaskull.*']),
    python_requires='>=3.6, <4',
    license='BSD 3-Clause License',
    zip_safe=False,
    project_urls={
        'Issues': 'https://github.com/akonieczny/flaskull/issues',
        'Source': 'https://github.com/akonieczny/flaskull',
    },
)
