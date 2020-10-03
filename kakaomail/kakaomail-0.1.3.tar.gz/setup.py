from setuptools import setup, find_packages

setup(
    name='kakaomail',
    version='0.1.3',
    description='send simple text using kakao mail',
    license='MIT',
    author='Kyunghonn',
    author_email='aloecandy@gmail.com',
    url='https://github.com/aloecandy/kakaomail',
    keywords=['kakao', 'mail','korean'],
    install_requires=[
        'email>=6.0.0a1'
    ],
    packages=find_packages(exclude=['tests'])
)