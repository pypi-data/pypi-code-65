from setuptools import setup, find_packages

setup(name='gsheetplot',
      version='1.2.2',
      description='Helps in Visualising Google Sheet Data',
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
