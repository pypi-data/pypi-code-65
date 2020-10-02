import setuptools

with open('russianCVparser/README.md', encoding='utf-8') as inf:
    ld = inf.read()

setuptools.setup(name='russianCVparser',
                 version='1.0rc5',
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
                 data_files=[
                     ('russianCVparser/cvparser/dicts', [
                         'russianCVparser/cvparser/dicts/occupations.txt',
                         'russianCVparser/cvparser/dicts/VUZY.txt',
                         'russianCVparser/cvparser/dicts/specs_only.txt'
                     ])
                 ],
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ],
                 python_requires='>=3.6',
                 )
