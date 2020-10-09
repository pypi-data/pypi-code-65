from setuptools import setup


setup(
    name="flask-util",
    version="0.0.1dev2",
    description="My personal Flask utility package.",
    url="https://github.com/Fakas/flask-util",
    author="Matthew Cazaly",
    author_email="matthewcaz@gmail.com",
    packages=["flask_util"],
    include_package_data=True,
    install_requires=[
        "Werkzeug==0.16.0",
        "Flask==1.1.2",
        "flask-restplus==0.13.0"
    ]
)
