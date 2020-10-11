from distutils.core import setup
setup(
  name = 'nextoff',         
  packages = [
    'nextoff', 
    'nextoff.test', 
    'nextoff.data', 
    'nextoff.models',
    'nextoff.train', 
    ],  # ! Important
  version = '0.1.1.9', # ! Always update
  license='MIT',        
  description = 'A package to experiment and tune keras hyperparameters', 
  author = 'Asapanna Rakesh',                   
  author_email = 'rakeshark22@gmail.com',      
  url = 'https://github.com/rakesh4real/nextoff', 
  download_url = 'https://github.com/rakesh4real/nextoff/archive/v0.1.1.9.tar.gz',
  keywords = ['Keras', 'hyperparameters', 'hyperparameters tuning'],   
  install_requires=[        
          'keras',
          'matplotlib'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)