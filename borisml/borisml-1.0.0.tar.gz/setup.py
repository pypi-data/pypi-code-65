import setuptools
import sys


if __name__ == '__main__':

    with open('README.md') as f:
        long_description = f.read()

    name = 'borisml'
    version = '1.0.0'

    author = 'Philipp Wirth & Igor Susmelj'
    author_email = 'philipp@lightly.ai'
    description = "This package has been deprecated, please install lightly."

    # keep entry points but display a message indicating that borisml has
    # migrated to lightly
    entry_points = {
        "console_scripts": [
            "boris-train = boris.cli.train_cli:entry",
            "boris-embed = boris.cli.embed_cli:entry",
            "boris-magic = boris.cli.boris_cli:entry",
            "boris-upload = boris.cli.upload_cli:entry",
            "boris-download = boris.cli.download_cli:entry",
        ]
    }

    # require lightly package which replaces borisml
    install_requires = ['lightly']

    project_urls = {
        'Python Package': 'https://pypi.org/project/lightly/',
        'Documentation': 'https://lightly.readthedocs.io',
        'Lightly': 'https://www.lightly.ai',
    }

    classifiers = [
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License"
    ]

    setuptools.setup(
        name=name,
        version=version,
        author=author,
        author_email=author_email,
        description=description,
        entry_points=entry_points,
        license='MIT',
        long_description=long_description,
        long_description_content_type='text/markdown',
        install_requires=install_requires,
        packages=setuptools.find_packages(),
        classifiers=classifiers,
        include_package_data=True,
        project_urls=project_urls,
    )

