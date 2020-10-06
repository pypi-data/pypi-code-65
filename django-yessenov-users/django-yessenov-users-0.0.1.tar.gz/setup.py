import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-yessenov-users",
    version="0.0.1",
    author="Nauryzbek Aitbayev",
    author_email="nauryzbek.aitbayev@yu.edu.kz",
    description="Данная библиотека содержит модель пользователя для всех проектов",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yessenovuniversity/django-users",
    packages=setuptools.find_packages(),
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
