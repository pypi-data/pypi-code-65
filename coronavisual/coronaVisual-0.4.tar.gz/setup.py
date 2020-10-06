from distutils.core import setup

setup(
  name = 'coronaVisual',
  packages = ['coronaVisual'],
  version = '0.4',
  license='MIT',
  description = 'Visualizing the Corona-Virus world data throughout time.',
  author = 'Yaniv Maimon',
  author_email = 'yanivmaimon18@gmail.com',
  url = 'https://github.com/yanivmm/coronaVisual',
  download_url = 'https://github.com/yanivmm/coronaVisual/archive/v_04.tar.gz',
  keywords = ['vizualization', 'data', 'coronavirus', 'COVID-19', 'Timeline','Corona','pandemic'],
  install_requires=[

          'pandas',
          'matplotlib',
          'seaborn',
      ],
  classifiers=[

    'Development Status :: 3 - Alpha',

    'Intended Audience :: Developers',

    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
  ],
)
