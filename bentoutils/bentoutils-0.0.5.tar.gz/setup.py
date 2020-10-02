import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='bentoutils',
    version='0.0.5',
    author='Mark Moloney',
    author_email='m4rkmo@gmail.com',
    description='Utilities for working with BentoML',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/markmo/bentoutils',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'BentoML==0.9.0',
        'click==7.1.2',
        'docker==4.3.1',
        'Jinja2==2.11.2',
        'kubernetes==11.0.0',
        'PyYAML==5.3.1',
        'simpletransformers==0.28.2',
        'stringcase==1.2.0',
        'tokenizers==0.7.0',
        'torch==1.6.0+cpu',
        'torchvision==0.7.0+cpu',
        'transformers==2.10.0',
    ],
    dependency_links=[
        'https://download.pytorch.org/whl/torch_stable.html',
    ],
    entry_points='''
        [console_scripts]
        bentopack=bentoutils.cli:pack
        deploy_to_knative=bentoutils.cli:deploy_to_knative
    ''',
    python_requires='>=3.6',
)
