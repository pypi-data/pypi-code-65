from distutils.core import setup

setup(
    name='mpimg',
    packages=['mpimg'],
    version='0.0.1',
    license='APACHE',
    description='generator for wechat mp platform',
    author='HuanCheng Bai',
    author_email='bestony@linux.com',
    url='https://github.com/bestony/mpimg',
    keywords=['image generate'],
    install_requires=[
        'click',
        'pillow'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
