from setuptools import setup, find_packages


setup(name='kayra',
      version='0.1',
    #   description="",
      url='https://gitlab.meridian.cs.dal.ca/data_analytics_dal/projects/kayra',
      author='Bruno Padovese',
      author_email='bpadovese@dal.ca',
      license='GNU General Public License v3.0',
      packages=['kayra'],
      install_requires=[
          'numpy',
          'tensorflow',
          'tensorflow-addons'
          ],
        setup_requires=['wheel'],
    #   tests_require=['pytest', ],
      include_package_data=True,
      zip_safe=False)