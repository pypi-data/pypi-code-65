from setuptools import setup, find_packages

setup(name='gsheetplot',
      version='1.3',
      description='Helps in Visualising Google Sheet Data. To Use this package, you should contain Cred.json which you will get from Developers Console and from that assign permission in Google Sheet to the mail in Cred and when initializing the class pass cred.json as first parameter and key (that you got from google sheet) as second parameter to Sheet_Plot of gsheetplot',
      long_description='Python Package Used to plot Bar Graph based on the data in Google Sheet',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
      ],
      keywords='Python-Data-Visualization Bar-Graph Python-Package Google-Sheet-Visualisation Matplotlib',
      url='https://github.com/ChaitanyaUndavalli/GSheetPlot',
      author='Undavalli Lalkrishnachaitanya',
      author_email='undavalli.14@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'matplotlib','gspread'
      ],
      include_package_data=True,
      zip_safe=False)
