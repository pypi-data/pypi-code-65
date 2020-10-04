from setuptools import setup, find_packages

setup(
    name = 'python-expression',
    version = '0.1',
    url = 'https://github.com/mwayi/python-expression',
    license = 'MIT',
    author = 'Mwayi Dzanjalimodzi',
    author_email = 'mr.mwayi@gmail.com',
    description = """
    Serialize and deserialize nested compound expression strings such as
    (a = 1 or (b = 2 and c = 3)) into parsable expression graphs such as
    [
        key:a operator:= value:1,
        conjunction:or, [
            key:b operator:= value:2,
            conjunction:and,
            key:c operator:= value:3
        ]
    ].
    """,
    packages = find_packages(
        include = ['expression.src']
    ),
    long_description = open('README.md').read(),
    long_description_content_type = "text/markdown",
    zip_safe = False
)
