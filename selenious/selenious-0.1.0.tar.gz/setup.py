from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    README = readme_file.read()

with open("HISTORY.rst") as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name="selenious",
    version="0.1.0",
    description="Enhancement to Selenium WebDriver for timeouts and more.",
    long_description_content_type="text/markdown",
    long_description=README + "\n\n" + HISTORY,
    license="MIT",
    packages=find_packages(),
    author="Mark Eklund",
    author_email="selenious@patnan.com",
    keywords=["Selenium", "WebDriver", "timeout"],
    url="https://github.com/bonafideduck/selenious",
    download_url="https://pypi.org/project/selenious/",
)

install_requires = [
    "selenium",
]

if __name__ == "__main__":
    setup(**setup_args, install_requires=install_requires)
