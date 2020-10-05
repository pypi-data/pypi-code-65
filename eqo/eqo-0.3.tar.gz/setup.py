import setuptools

setuptools.setup(name='eqo',
      version='0.3',
      description='Manage connections to FPGAs running EQO',
      author=u'Sascha M\u00fccke',
      author_email='sascha.muecke@tu-dortmund.de',
      license='GNU GPLv3',
      packages=setuptools.find_packages(),
      python_requires='>=3.6',
      install_requires=['bitarray', 'numpy', 'tqdm'])
