from setuptools import find_packages, setup
ver = '0.1'
setup(
    name='genuisfinder',
    packages=find_packages(),
    version=ver,
    description='Lyrics finder from Genuis',
    author='Fichee_SS',
    license='ACSL',
    install_requires=['beautifulsoup4'],
    url='https://github.com/FicheeSS/genuisfinder',
    download_url='https://github.com/FicheeSS/genuisfinder/archive/'+ ver+'.tar.gz',
)
classifiers =[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development',
    'License :: ACLS License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]