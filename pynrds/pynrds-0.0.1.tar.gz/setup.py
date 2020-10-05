from setuptools import setup

setup(
    name='pynrds',
    version='0.0.1',
    description='A Complete Python Wrapper for the NAR NRDS API Service',
    long_description='',
    url='https://github.com/mansard/pynrds',
    author='Jeremey Bingham',
    author_email='info@mansard.net',
    packages=[],
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