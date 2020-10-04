from distutils.core import setup
setup(
  name = 'PyFacileGui',         # How you named your package folder (MyLib)
  packages = ['PyFacileGui'],   # Chose the same as "name"
  version = '0.5',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Simpler life with most modules combined.',   # Give a short description about your library
  author = 'Jerry Hu',                   # Type in your name
  author_email = 'bestfit.jerry.wu@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/AccessRetrieved/PyFacileGui',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/AccessRetrieved/PyFacileGui/archive/0.5.tar.gz',    # I explain this later on
  keywords = ['pygui', 'PyGui', 'python', 'Python', 'easy', 'combined', 'modules', 'pyfacilegui', 'PyFacileGui', 'Pyfacilegui'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pyautogui',
          'keyboard',
          'yagmail',
          'rumps'
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.6',    #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8'
  ],
)