from setuptools import setup, find_packages
VERSION = '0.0.1'
setup(name='github_download',
      version=VERSION,
      description="a command line tool for camel case",
      long_description='a python command tool for camel case',
      classifiers=[],
      keywords='Github_Download',
      author='',
      author_email='1223411083@qq.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=['requests','lxml','Beautifulsoup4'],
      entry_points={
          'console_scripts': [
              'git_down = Github_download.Git_down:main'
          ]
      }
)