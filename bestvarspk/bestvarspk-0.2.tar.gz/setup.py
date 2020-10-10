from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='bestvarspk',
      version='0.2',
      description='Bestvars feature_selection methods',
      packages=['bestvarspk'],
      long_description=long_description,
      long_description_content_type="text/markdown",
      author = 'Gutelvam Rodrigues de Jesus',
      author_email = 'gutto.rdj@gmail.com',
      zip_safe=False)