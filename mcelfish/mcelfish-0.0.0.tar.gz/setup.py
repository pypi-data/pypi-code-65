import setuptools

setuptools.setup(
    version="0.0.0",
    name="mcelfish",
    packages=["mcelfish"],
    entry_points={
        "console_scripts": [
            "mcelfish=mcelfish:main",
            "mcelfish-gen=mcelfish:generate",
            "mcelfish-cs=mcelfish:cs_z",
            "mcelfish-z=mcelfish:cs_z",
        ]
    },
)
