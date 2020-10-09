import io
from setuptools import setup, find_packages



setup(
    name='gsheet_image_generator',
    version='1.0.0',
    author='shivachandra',
    author_email='k.s9908725092@gmail.com',
    url='https://github.com/shivachandrakante/gsheet_image_generator',
    description='An awesome package which helps us in creating a graph from Google Sheets and stores them as image',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords='spreadhseets google api v4 wrapper csv pandas image_generator',
    packages=find_packages(),
    license='LICENSE',
    platforms='any',
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*',
    include_package_data=True,
    install_requires=
      [
        "google-auth-oauthlib==0.4.1",
        "google-auth-httplib2==0.0.4",
        "gsheets >= 0.5.1",
        "numpy",
        "pandas",
        "matplotlib",
        "seaborn",
        'google-api-python-client<1.8; python_version < "3"',
        'google-api-python-client; python_version >= "3"',
        'oauth2client>=1.5.0',
      ],
)