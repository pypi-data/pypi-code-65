import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pa_math-liuxinglu", # Replace with your own username
    version="0.0.1",
    author="liuxinglu",
    license='MIT',
    author_email="liuxinglu675@sina.com",
    description="数学部测试成绩转换专用工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/liuxinglu/pa_math",
    install_requires=[
        'openpyxl>=3.0.5',
        'xlrd>=1.2.0'
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
