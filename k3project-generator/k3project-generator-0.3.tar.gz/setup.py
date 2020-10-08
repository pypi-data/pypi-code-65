from setuptools import setup, find_packages

setup(
    name='k3project-generator',
    version='0.3',
    packages=find_packages(exclude=["tests"]),
    # Searches and includes .md files within the installation
    package_data={
        '' : ['*.md', '*.txt']
    },
    #include_package_data=True,
    # libraries from PyPI that this project depends on
    install_requires=[
        "pytest"
    ],
    entry_points={
        'console_scripts': [
            'k3project-generator = k3project_generator.main.generate_project:main'
        ]
    }
)

