from setuptools import setup, find_packages

setup(name='gsheets_plot',
      version='0.2.1',
      description='Plot data from Google Sheets',
      long_description='Fetch Google sheets and plot the required columns',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved',
        'Programming Language :: Python :: 3.7',
      ],
      keywords='google sheets plot',
      url='https://github.com/akhipachi/gsheets_plot',
      author='Akhilesh Pachipulusu',
      author_email='p.akhilesh99@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'matplotlib','gsheets','pandas',
      ],
      include_package_data=True,
      zip_safe=False)