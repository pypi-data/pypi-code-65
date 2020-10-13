
from distutils.core import setup
setup(
    name='crawler_toolz',         # How you named your package folder (MyLib)
    packages=['crawler_toolz'],   # Chose the same as "name"
    version='0.2.2.2',      # Start with a small number and increase it with every change you make
    license='GNU General Public License v3.0',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='Proxy rotation with PostgreSQL',   # Give a short description about your library
    author='Leo',                   # Type in your name
    author_email='thegoldcat5@gmail.com',      # Type in your E-Mail
    url='https://github.com/goldcvt/crawler_tools',   # Provide either the link to your github or to your website
    download_url='https://github.com/goldcvt/archive/crawler_tools/v_0.2.2.2.tar.gz',    # I explain this later on
    keywords=['scraping', 'web-scraping', 'PostgreSQL'],   # Keywords that define your package best
    install_requires=[            # I get to this in a second
        'psycopg2'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',      # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',   # Again, pick a license
        'Programming Language :: Python :: 3.6',
    ],
)