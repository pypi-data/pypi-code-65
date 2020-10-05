from distutils.core import setup

setup(
    name='egter',
    version='0.3',
    packages=['egter', 'egter.crypt', 'egter.crypt.enigma', 'egter.crypt.steganography', 
    			'egter.crypt.hash'],
    url='https://notabug.org/EgTer/egter-py',
    license='GNU GPL v3',
    author='EgTer',
    author_email='annom2017@mail.ru',
    description='My collection of my tools'
)
