"""
Setup for gd library
"""

from setuptools import setup, find_packages


def main():
    """Main function"""
    with open("requirements.txt") as req_file:
        requirements = [r.strip() for r in req_file if r.strip() != ""]

    setup(
        name="gd",
        author="Tomas Votava",
        version="0.0.8",
        description="Python GoodData SDK library",
        packages=find_packages(),
        install_requires=requirements,
        author_email="tomas.votava@bizztreat.com",
        url="https://bizztreat.com",
        project_urls={
            "Git": "https://gitlab.com/bizztreat/dev/pygd",
            "Documentation": "https://bizztreat.gitlab.io/dev/pygd",
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )


if __name__ == "__main__":
    main()
