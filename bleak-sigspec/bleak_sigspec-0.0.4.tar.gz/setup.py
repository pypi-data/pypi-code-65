from setuptools import setup


def readme():
    with open('README.md', 'r', encoding="utf-8") as f:
        return f.read()


setup(name='bleak_sigspec',
      version='0.0.4',
      description='Bleak SIG Bluetooth Low Energy Characteristics Specification Formatter',
      long_description=readme(),
      long_description_content_type='text/markdown',
      url='http://github.com/Carglglz/bleak_sigspec',
      author='Carlos Gil Gonzalez',
      author_email='carlosgilglez@gmail.com',
      classifiers=[
                  'Intended Audience :: Developers',
                  'Intended Audience :: Science/Research',
                  'Intended Audience :: Education',
                  'License :: OSI Approved :: MIT License',
                  'Programming Language :: Python :: 3.6',
                  'Programming Language :: Python :: 3.7',
                  'Programming Language :: Python :: 3.8',
                  'Topic :: System :: Monitoring',
                  'Topic :: Scientific/Engineering',
                  'Topic :: Software Development :: Embedded Systems'],
      license='MIT',
      packages=['bleak_sigspec'],
      zip_safe=False,
      include_package_data=True,
      install_requires=['bleak>=0.8.0'])
