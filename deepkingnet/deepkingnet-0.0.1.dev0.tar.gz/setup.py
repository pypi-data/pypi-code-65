from setuptools import setup, find_packages

setup(
    name="deepkingnet",
    version='0.0.1_dev',
    description='A command line tool to classify nucleotide sequences as prokaryotic or eukaryotic.',
    url='https://github.com/bhattlab/DeepKingNet',
    author="Matt Durrant",
    author_email="mdurrant@stanford.edu",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click==7.0',
        'biopython==1.76',
        'tensorflow==2.1.0'
    ],
    zip_safe=False,
    entry_points = {
        'console_scripts': [
            'dkn = deepkingnet.main:cli'
        ],
}
)
