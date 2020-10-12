from setuptools import setup
import setuptools 

def www():
    print('www')


setup(
    name='sync_setting',
    version='0.0.4',
    author='wwc129',
    author_email='3157576559@qq.com',
    packages=setuptools.find_packages(),
    # package_dir={
    #     'apis': "./apis",
    #     'locations': './locations',
    #     'utils': './utils'
    # },
    entry_points={
        'console_scripts': ['main=scripts.main:run']
    }
)
