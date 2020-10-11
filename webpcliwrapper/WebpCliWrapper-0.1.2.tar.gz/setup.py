from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='WebpCliWrapper',
    version='0.1.2',
    description='A CLI Wrapper to use webp easily',
    long_description_content_type="text/markdown",
    long_description=README,
    license='MIT',
    packages=find_packages(),
    author='Florian Erbs',
    author_email='f@flopana.com',
    keywords=['webp', 'webp-cli-wrapper'],
    url='https://gitlab.aptinstall.de/flopana/webp-cli-wrapper',
    download_url='https://pypi.org/project/webp-cli-wrapper/'
)


if __name__ == '__main__':
    setup(**setup_args)