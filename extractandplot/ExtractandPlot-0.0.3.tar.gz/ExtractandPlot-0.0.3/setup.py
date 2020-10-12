from setuptools import setup, find_packages

classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
    ]
setup(
      name='ExtractandPlot',
      version='0.0.3',
      description='Download file from google drive and Plot it using scatter plot',
      long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
      url='',  
      author='Hardik Choudhary',
      author_email='hardikchoudhary2698@gmail.com',
      license='MIT', 
      classifiers=classifiers,
      keywords='', 
      packages=find_packages(),
      install_requires=['Python>=3.0',
                        'Pandas',
                        'Matplotlib',
                        'google_drive_downloader'
                        ] 
)