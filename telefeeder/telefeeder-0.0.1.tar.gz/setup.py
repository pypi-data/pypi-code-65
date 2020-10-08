from setuptools import setup, find_packages

classifiers =[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3',
          'Topic :: Communications :: Email',
          'Topic :: Office/Business',
          'Topic :: Software Development :: Bug Tracking',
          ]

setup(name='telefeeder',
      version='0.0.1',
      description='A simple python script to send your RSS feeds to your Telegram channel',
      long_description = open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
      author='Nosratulla Mohammadi',
      author_email='nh.afgboy@gmail.com',
      url='',
      license='MIT',
      keywords = ['telegram', 'rss', 'feed'],
      classifiers = classifiers,
      install_requires=['telegram-bot-api','feedparser','html2text','schedule'],
      packages = find_packages()
      )
