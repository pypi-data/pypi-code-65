# Copyright 2020 Scale Plan Yazılım A.Ş.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name='spce',
    version='0.3.0',
    packages=['spce'],
    url='https://github.com/scaleplandev/spce-python',
    license='Apache 2.0',
    author='ScalePlan Engineering',
    author_email='dev@scaleplan.io',
    description="ScalePlan's CloudEvents implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
    ],
    keywords='cloudevents,scaleplan,cloud,events,event',
    tests_require=['pytest', 'coverage', 'pytest-cov', 'avro'],
    extras_require={
        'avro': ['avro>=1.10']
    }
)
