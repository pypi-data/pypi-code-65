from setuptools import setup, find_packages

setup(
    name="fast-dict",
    version="1.0.3",
    description="A class that operates quickly on dict",
    long_description="A class that operates quickly on dict",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8'
    ],
    keywords="",
    author="_凌川",
    author_email="2282440078@qq.com",
    url="",
    packages=['fast_dict'],
    install_requires=[
        'jsonpath>=0.82'
    ],
    include_package_data=True,
    zip_safe=True,
    # entry_points={
    #     "console_scripts": [
    #         "fast_dict = ",
    #     ]
    # },
)
