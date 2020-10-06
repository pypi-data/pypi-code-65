"""Configure distribution package."""
import setuptools


with open('README.md', 'r') as f:
    long_description = f.read()

install_requires = []
with open('requirements.txt') as f:
    for line in f:
        line = line.strip()
        install_requires.append(line)

setuptools.setup(
    author='John Tucker',
    author_email='john@larkintuckerllc.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    description='A small example package',
    install_requires=install_requires,
    long_description=long_description,
    long_description_content_type='text/markdown',
    name='examplepkglarkintuckerllc',
    license="MIT",
    packages=setuptools.find_packages(),
    python_requires='>=3.8',
    url='https://github.com/larkintuckerllc/examplepkglarkintuckerllc',
    version='0.0.3',
)
