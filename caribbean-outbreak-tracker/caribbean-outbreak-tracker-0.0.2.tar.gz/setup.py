from setuptools import setup, find_packages

version=__import__('outbreak_tracker').__version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="caribbean-outbreak-tracker",
    version=version,
    author="Obika Gellineau",
    author_email="obikagellineau@gmail.com",
    description="Django package for tracking pandemic outbreaks in the Caribbean.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/obikag/caribbean-outbreak-tracker",
    packages=find_packages(exclude=["testproject"]),
    install_requires=[
        "Django>=2.0",
        "django-countries>=6.0,<7.0"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Environment :: Web Environment",
        "Topic :: Internet",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content"
    ],
    python_requires='>=3.6',
)