import setuptools


def get_long_description():
    with open("README.rst") as file:
        return file.read()

setuptools.setup(
    name="django-crispy-views",
    version="1.0.0",
    description="crispy views for django.",
    long_description=get_long_description(),
    url="https://github.com/monim67/django-crispy-views",
    author="Munim Munna",
    author_email="monim67@yahoo.com",
    license="MIT",
    keywords="crispy, views",
    packages=["crispy_views"],
    install_requires=["django>=2.0", "django-crispy-forms>=1.8.1", "django-filter>=2.2.0", "django-tables2>=2.2.1"],
    python_requires=">=3",
    classifiers=[
        "Intended Audience :: Developers",
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 3.0",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Utilities",
    ],
)
