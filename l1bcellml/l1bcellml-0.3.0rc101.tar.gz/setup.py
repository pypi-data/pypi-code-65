""" libCellML Library: A library for the parsing, printing, and manipulation
of CellML 2.0 compliant models.

"""

classifiers = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
Intended Audience :: Education
Intended Audience :: Science/Research
License :: OSI Approved :: Apache Software License
Programming Language :: Python
Operating System :: Microsoft :: Windows
Operating System :: Unix
Operating System :: MacOS :: MacOS X
Topic :: Software Development :: Libraries :: Python Modules
"""

from setuptools import setup
from setuptools.dist import Distribution

doclines = __doc__.split("\n")


class BinaryDistribution(Distribution):
    def is_pure(self):
        return False

    def has_ext_modules(self):
        return True


setup(
    name='l1bcellml',
    version='0.3.0rc101',
    author='libCellML developers',
    author_email='libcellml@googlegroups.com',
    packages=['libcellml'],
    package_data={'libcellml': ['libcellml.0.3.0-rc.101.dylib', '_analyser.so', '_analyserequation.so', '_analyserequationast.so', '_analysermodel.so', '_analyservariable.so', '_annotator.so', '_component.so', '_componententity.so', '_entity.so', '_enums.so', '_generator.so', '_generatorprofile.so', '_importer.so', '_importsource.so', '_importedentity.so', '_issue.so', '_logger.so', '_model.so', '_namedentity.so', '_parser.so', '_printer.so', '_reset.so', '_types.so', '_units.so', '_validator.so', '_variable.so', '_version.so']},
    url='http://cellml.org',
    license='Apache Software License',
    description=doclines[0],
    classifiers=classifiers.split("\n"),
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    distclass=BinaryDistribution,
    include_package_data=True,
    zip_safe=False,
)
