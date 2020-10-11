from distutils.core import setup

setup(
    name="lime-uow",
    version="1.9",
    packages=["lime_uow"],
    url="https://github.com/MarkStefanovic/lime-uow",
    license="MIT",
    author="Mark Stefanovic",
    author_email="markstefanovic@hotmail.com",
    description="Framework to support the Unit-of-Work pattern",
    package_data={
        "lime_uow": ["py.typed"]
    },
    include_package_data=True,
)
