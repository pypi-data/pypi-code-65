import setuptools

setuptools.setup(
    name='gicd',
    version='1.0.2',
    author='Zeke Marffy',
    author_email='zmarffy@yahoo.com',
    packages=setuptools.find_packages(),
    url='https://github.com/zmarffy/gicd',
    license='LICENSE.txt',
    description='Python decorator that will automatcially create an issue on GitHub if a decorated function throws an exception',
    python_requires='>=3.6',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'zmtools'
    ],
)