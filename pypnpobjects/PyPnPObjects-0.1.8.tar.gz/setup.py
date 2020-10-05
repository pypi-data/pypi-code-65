from setuptools import setup
import json
import os

def readme():
    with open('./README.md') as readme_fp:
        README = readme_fp.read()
    return README

class SetupMeta:
    def __init__(self):
        self.__dict__.update(
            json.loads(
                open(
                    os.path.abspath(
                        os.path.join(
                            os.path.dirname(__file__),
                            'METADATA.json'
                        )
                    )
                ).read()
            )
        )

meta = SetupMeta()

if meta.development_status == 1:
    status = 'Planning'
elif meta.development_status == 2:
    status = 'Pre-Alpha'
elif meta.development_status == 3:
    status = 'Alpha'
elif meta.development_status == 4:
    status = 'Beta'
elif meta.development_status == 5:
    status = 'Production/Stable'
elif meta.development_status == 6:
    status = 'Mature'
else:
    status = 'Inactive'


setup(
    name=meta.module_name,
    version=meta.version_info,
    description='''
        This is a simple python module to get the detail level information about Win32 WMI objects.
        Current Version of the module is {0}
        This module has been compiled with Python - {1}
    '''.format(meta.version_info, '.'.join(map(lambda e: str(e), os.sys.version_info[0:3]))),
    long_description=readme(),
    long_description_content_type='text/markdown',
    url="https://github.com/antaripchatterjee/PyPnPObjects",
    author="Antarip Chatterjee",
    author_email="antarip.chatterjee22@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Environment :: Console",
        "Development Status :: %d - %s"%(meta.development_status, status),
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: System :: Hardware :: Hardware Drivers"
    ],
    packages=["pypnpobjects"],
    include_package_data=True,
    entry_points={
        "console_scripts" : [
            "get-pnpobjects=pypnpobjects.main:main"
        ]
    }
)