from setuptools import setup
from setuptools import find_packages
import time

setup(
    name='sammaNLP',
    version=time.strftime('%Y.%m.%d.%H.%M.%S'),
    packages=find_packages('/media/gentai/7c1cdd31-07a1-4f49-9368-85be4d4787b51/customer/sammaProject/sammaNLP/'),
    url='http://baidu.com',
    license='MIT',
    author='samma',
    author_email='13336502700@163.com',
    description='some common tool for nlp task',
    install_requires=[
        'torch==1.2.0',
        'pandas==1.1.2',
        'scikit-learn==0.23.2',
        'seqeval==0.0.12',
    ],
)
