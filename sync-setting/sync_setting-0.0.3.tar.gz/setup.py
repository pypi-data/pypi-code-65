from setuptools import setup


def www():
    print('www')


setup(
    name='sync_setting',
    version='0.0.3',
    author='wwc129',
    author_email='3157576559@qq.com',
    packages=['apis', 'locations', 'utils'],
    package_dir={
        'apis': "./apis",
        'locations': './locations',
        'utils': './utils'
    },
    entry_points={
        'console_scripts': ['main=scripts.main:run']
    }
)
