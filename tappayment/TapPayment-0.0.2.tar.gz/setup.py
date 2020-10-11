from setuptools import setup

with open('README.md') as readme:
    readme_content = readme.read()

setup(
    name="TapPayment",
    version="0.0.2",
    description="Tap Payment Python Client",
    long_description=readme_content,
    long_description_content_type='text/markdown',
    url="https://github.com/Qasem-h/tappayment-python",
    author="Qasem hajizadeh",
    license="MIT",
    install_requires=["requests"],
    include_package_data=True,
    package_dir={'tappayment': 'tappayment', 'tappayment.resources': 'tappayment/resources',"tappayment.constants": 'tappayment/constants'},
    packages=['tappayment', 'tappayment.resources',"tappayment.constants"],
    keywords='tappayment gateway, tap.company, tappayment gosell, gosell',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        # List of supported Python versions
        "Programming Language :: Python",
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)