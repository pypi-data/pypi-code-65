import os


def configuration(parent_package='', top_path=None):
    import numpy
    from numpy.distutils.misc_util import Configuration

    config = Configuration('dependency', parent_package, top_path)
    libraries = []
    if os.name == 'posix':
        libraries.append('m')
    config.add_extension("_quad_tree",
                         sources=["_quad_tree.pyx"],
                         include_dirs=[numpy.get_include()],
                         libraries=libraries)
    return config
