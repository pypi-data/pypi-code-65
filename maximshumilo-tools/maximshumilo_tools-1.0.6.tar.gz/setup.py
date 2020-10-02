from setuptools import setup, find_packages

with open('README.rst', 'r', encoding='utf-8') as readme_file:
    long_desc = readme_file.read()

with open('LICENSE.txt', 'r', encoding='utf-8') as license_file:
    license_file = license_file.read()


def get_requires():
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as source_file:
            result = [item.strip() for item in source_file.readlines()]
    except FileNotFoundError:
        with open('maximshumilo_tools.egg-info/requires.txt', 'r', encoding='utf-8') as requires_file:
            result = [item.strip() for item in requires_file.readlines()]
    return result


setup(
    name='maximshumilo_tools',
    version='1.0.6',
    url='https://github.com/maximshumilo/tools',
    license=license_file,
    author='Shumilo Maksim',
    author_email='shumilo.mk@gmail.com',
    description='My tools for developing',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=get_requires(),
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Alpha',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        'Programming Language :: Python :: 3.8',
    ],
)
