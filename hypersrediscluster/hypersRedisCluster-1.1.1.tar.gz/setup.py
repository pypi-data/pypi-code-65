import setuptools

from hypersRedisCluster import __version__

setuptools.setup(
    name="hypersRedisCluster",
    version=__version__,
    author="yingzhe.zhang",
    author_email="yingzhe.zhang@mail.hypers.com",
    description="support redis cluster",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    python_requires=">=3.6",
    install_requires=["redis-py-cluster", "django-redis"],
    zip_safe=False,
)
