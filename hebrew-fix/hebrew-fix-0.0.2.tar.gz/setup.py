from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='hebrew-fix',
    version='0.0.2',
    description="With this module you can fix your hebrew broken encode",
    url='https://lamed-oti2.ml/',
    author='Kobi Shutzi',
    author_email='shutzi@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='Hebrew-fixer',
    packages=find_packages(),
    install_requires=['requests']
)