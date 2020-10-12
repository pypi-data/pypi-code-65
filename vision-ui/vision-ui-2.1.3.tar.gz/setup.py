# encoding: utf-8
import io
import os
import sys
from shutil import rmtree

from setuptools import Command, find_packages, setup

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'service', '__about__.py'), encoding='utf-8') as f:
    exec(f.read(), about)

with io.open("README.md", encoding='utf-8') as f:
    long_description = f.read()

install_requires = [
    "opencv-python==4.2.0.32",
    "numpy==1.19.1",
    "Flask==1.0.2",
    "Flask-Cors==3.0.7",
    "pillow==6.2.0",
    "paddlepaddle==1.8.4",
    "gunicorn==20.0.4",
    "onnxruntime==1.4.0",
    "pyclipper==1.2.0",
    "shapely==1.7.0"
]


class UploadCommand(Command):
    """ Build and publish this package.
        Support setup.py upload. Copied from requests_html.
    """

    user_options = []

    @staticmethod
    def status(s):
        """Prints things in green color."""
        print("\033[0;32m{0}\033[0m".format(s))

    def initialize_options(self):
        """ override
        """
        pass

    def finalize_options(self):
        """ override
        """
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        # self.status('Publishing git tags…')
        # os.system('git tag v{0}'.format(about['__version__']))
        # os.system('git push --tags')

        sys.exit()


setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    license=about['__license__'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
    # packages=['dbnet_crnn','service'],
    packages=find_packages(),

    package_data={
        '': ["README.md"],
        'dbnet_crnn': ['dbnet_crnn/model/det/model', 'dbnet_crnn/model/det/params', 'dbnet_crnn/model/rec/model',
                       'dbnet_crnn/model/rec/params', 'dbnet_crnn/ppocr/utils/keys.txt'],
    },
    data_files=[('dbnet_crnn/model/det', ['dbnet_crnn/model/det/model', 'dbnet_crnn/model/det/params']),
                ('dbnet_crnn/model/rec', ['dbnet_crnn/model/rec/model', 'dbnet_crnn/model/rec/params']),
                ('dbnet_crnn/ppocr/utils', ['dbnet_crnn/ppocr/utils/keys.txt'])],
    keywords='A line-oriented image diff algorithm',
    install_requires=install_requires,
    extras_require={},
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    # entry_points={
    #     'console_scripts': [
    #         'ate=httprunner.cli:main_hrun',
    #         'httprunner=httprunner.cli:main_hrun',
    #         'hrun=httprunner.cli:main_hrun',
    #         'locusts=httprunner.cli:main_locust'
    #     ]
    # },
    # $ setup.py upload support.
    cmdclass={
        'upload': UploadCommand
    }
)
