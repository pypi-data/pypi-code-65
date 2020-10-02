from setuptools import setup
setup(
  name = 'slicednormals',
  packages = ['slicednormals'],
  version = '0.1.16-alpha',
  license='gpl-3.0',
  description = 'Library for fitting basic and scaled sliced normal distributions',
  author = 'Alexander Wimbush',
  author_email = 'alexanderpwimbush@gmail.com', 
  url = 'https://github.com/Institute-for-Risk-and-Uncertainty/Sliced-Normals-Python',
  download_url = 'https://github.com/Institute-for-Risk-and-Uncertainty/Sliced-Normals-Python/archive/0.1.16-alpha.tar.gz', 
  keywords = ['dependence', 'expansion', 'density'], 
  install_requires=[
          'numpy',
		  'scipy'
      ],
)