from setuptools import setup

def www():
    print('www')

setup(
    name='sync_setting',
    version='0.0.1',
    author='wwc129',
    author_email='3157576559@qq.com',


    entry_points = {
        'console_scripts': ['main=scripts.main:run']
    }
)
