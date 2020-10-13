import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='pynrds',
    version='0.0.2',
    description='A Complete Python Wrapper for the NAR NRDS API Service',
    install_requires=['requests', 'pandas', 'numpy', 'mimesis', 'faker', 'delorean'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mansard/pynrds',
    author='Jeremey Bingham',
    author_email='info@mansard.net',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'Development Status :: 1 - Planning'],
    python_requires='>=3.7',
    py_modules=['pynrds'],
    entry_points='''
        [console_scripts]
        pynrds = pynrds:pynrds
    '''
)
