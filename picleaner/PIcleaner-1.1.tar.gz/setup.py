from setuptools import setup

setup(name='PIcleaner',
      version='1.1',
      description='Clean the dirty things in our lovely data.',
      url='',
      author='Martin Kirilov, Dung Le (Eric)',
      author_email='martin.kirilov@pandoraintelligence.com, dung.le@pandoraintelligence.com',
      license='Pandora Intelligence',
      packages=['PIcleaner'],
      install_requirements=[
          'clean-text[gpl]',
          'spacy',
          'lxml'
      ],
      zip_safe=False)