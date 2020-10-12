from setuptools import setup, find_packages

setup(
    name="cloud_queue_worker",
    version="0.0.6",
    author="Enlaps Open Source",
    author_email="contact@enlaps.fr",
    description="Library to create workers for aws, azure and gcp queue services",
    url="https://gitlab.com/enlaps-public/web/cloud_queue_worker",
    install_requires=[
        'boto3>=1.14.63',
        'marshmallow>=3.8.0'
    ],
    packages=find_packages(),
    extras_require={
        'dev': [
            'pytest',
            'mypy',
            'pylint'
        ]
    },
    python_requires='>=3.6',
)
