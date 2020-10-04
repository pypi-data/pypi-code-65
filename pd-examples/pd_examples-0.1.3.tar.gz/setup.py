from distutils.core import setup

setup(
    name='pd_examples',  # How you named your package folder
    packages=['pd_examples'],  # Chose the same as "name"
    version='0.1.3',
    license='mit',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='collection of pandas and numpy examples',
    author='Hui Wang',
    author_email='che220@yahoo.com',
    url='https://github.com/che220/pd_examples.git',
    # create release on github and copy the link of .tar.gz
    download_url='https://github.com/che220/pd_examples/archive/0.1.3.tar.gz',
    keywords=['Python', 'pandas', 'numpy', 'example'],
    install_requires=['pandas', 'numpy'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3'  # Specify which pyhton versions that you want to support
    ],
)
