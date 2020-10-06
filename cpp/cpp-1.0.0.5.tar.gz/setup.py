from setuptools import setup

setup(
    name='cpp',
    version='1.0.0.5',
    description='Primera version de cpp!',
    packages = ['cpp'],
    license='MIT',
    author_email='erick.alvarez.met@gmail.com',
    download_url='https://github.com/3r1ck10/cpp/archive/v1.0.0.tar.gz',
    install_requires=['numpy',
    'pandas','matplotlib','xarray','seaborn','scikit-learn','netcdf4'],
    classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
