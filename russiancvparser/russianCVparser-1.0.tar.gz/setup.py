import setuptools

with open('russianCVparser/README.md', encoding='utf-8') as inf:
    ld = inf.read()

setuptools.setup(name='russianCVparser',
                 version='1.0',
                 description='Parser for CV in russian language. Supported formats: pdf, txt, docx',
                 long_description=ld,
                 long_description_content_type="text/markdown",
                 packages=setuptools.find_packages(),
                 author_email='onsunday1703@gmail.com',
                 install_requires=[
                     'natasha',
                     'pdfminer',
                     'docx2txt'
                 ],
                 package_data={'russianCVparser': ['*.txt']},
                 include_package_data=True,
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ],
                 python_requires='>=3.6',
                 )
