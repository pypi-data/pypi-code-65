from setuptools import setup

with open('README.md', 'r') as f:
    readme = f.read()

setup(
    name='better-progress',
    version='1.0.3.post1',
    description='Customize and create a progress bar string.',
    packages=['better_progress'],
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Typing :: Typed',
        'Environment :: Console',
        'Development Status :: 5 - Production/Stable'
    ],
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/LoganGerber/better-progress',
    author='Logan Gerber',
    author_email='logangerber1014@yahoo.com'
)
