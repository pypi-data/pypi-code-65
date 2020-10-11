from setuptools import setup, find_packages


classifiers = {
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
}

setup(
    name="plotursheet",
    version="0.0.2",
    description="A Python package to plot data from google sheets",
    long_description='\n\n'.join([
        open('README.txt').read(),
        open('CHANGES.txt').read(),
        ]),
    long_description_content_type='text/markdown',
    url="https://github.com/fat-a-lity/plotursheet",
    author="Varun Chandran",
    author_email="varunjay7@gmail.com",
    license="MIT",
    classifiers= classifiers,
    keywords='gsheets',
    packages=find_packages(),
    include_package_data=True,
    install_requires=["gsheets","pandas","numpy","matplotlib.com"]
)