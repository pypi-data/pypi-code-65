from distutils.core import setup

setup(
    name='Optimizers',  # How you named your package folder (MyLib)
    packages=['Optimizers'],  # Chose the same as "name"
    version='v1.9',  # Start with a small number and increase it with every change you make
    license='GNU General Public License v3.0',
    # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='A collection of examples for learning mathematical modelling',
    # Give a short description about your library
    author='David S.W. Lai',  # Type in your name
    author_email='davidswlai@outlook.com',  # Type in your E-Mail
    url='https://github.com/davidswlai/',  # Provide either the link to your github or to your website
    download_url='https://github.com/davidswlai/Optimizers/releases/latest',  # I explain this later on
    keywords=['Optimizers', 'Mathematical Models', 'Logistics', 'Routing', 'Scheduling'],
    # Keywords that define your package best
    install_requires=[
        'requests>=2.24.0',
        'aiohttp>aiohttp>=3.6.2',
        'asyncio>=3.4.3'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
)
