from setuptools import setup

setup(name='easyplot1',
      version='0.2',
      description='access sheet from drive and plot a chart',
      url='https://github.com/maylad31/easyplot',
      author='Mayank L.',
      author_email='mynameladdha@gmail.com',
      license='MIT',
      packages=['easyplot1'],
      install_requires=[
          'gsheets','pandas'
      ],
      zip_safe=False)

