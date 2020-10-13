from setuptools import setup

if __name__ == "__main__":
    setup(
        packages=["plantuml_wrapper"],
        install_requires=[],
        name="plantuml-wrapper",
        description="os independent wrapper around plantuml.jar",
        long_description="os independent wrapper around plantuml.jar",
        version="0.0.3",
        author="Christian Winger",
        author_email="c@wingechr.de",
        url="https://github.com/wingechr/plantuml-wrapper",
        classifiers=[
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Operating System :: OS Independent",
        ],
        entry_points={"console_scripts": ["plantuml = plantuml_wrapper.__main__:main"]},
    )
