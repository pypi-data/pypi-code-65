from distutils.core import setup


with open('README.rst') as f:
    readme = f.read()

setup(
    name='egter',
    version='0.3.4',
    packages=['egter', 'egter.crypt', 'egter.crypt.enigma', 'egter.crypt.steganography', 
    			'egter.crypt.hash', 'egter.handlers'],
    url='https://notabug.org/EgTer/egter-py',
    license='GNU GPL v3',
    author='EgTer',
    long_description=readme,
    author_email='annom2017@mail.ru',
    description='My collection of my tools'
)
