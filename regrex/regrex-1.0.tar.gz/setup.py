from distutils.core import setup
setup(
  name = 'regrex',         # How you named your package folder 
  packages = ['regrex'],   # Chose the same as "name"
  version = '1.0',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'regression made easy with regrex !',   # Give a short description about your library
  author = 'rushan7750',                   # Type in your name
  author_email = 'shanrsjmax@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/rushan7750/regress',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/rushan7750/regress/archive/0.9.tar.gz',    # I explain this later on
  keywords = ['regress', 'simple', 'regrex'],   # Keywords that define your package best
  install_requires=[            # required libraries
          'scikit-learn',
          'colorama',
          'termcolor'
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which python versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)
