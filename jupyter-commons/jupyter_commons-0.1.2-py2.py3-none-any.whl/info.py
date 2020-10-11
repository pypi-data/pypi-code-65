# -*- coding: utf-8 -*-

"""Information related functions."""

import os
import platform
from platform import python_version


def system_info(globs: dict) -> None:
    """ Print versions of imported packages.

    Looks for select packages if imported and prints version info.

    :param globs: globals() of calling code.
    """
    print("-- System --")
    print("os name: %s" % os.name)
    print("system: %s" % platform.system())
    print("release: %s" % platform.release())
    print()
    print("-- Python --")
    print("version: %s" % python_version())
    print()
    print("-- Python Packages --")
    if 'jupyterlab' in globs:
        print("jupyterlab==%s" % globs['jupyterlab'].__version__)
    if 'np' in globs:
        print("numpy==%s" % globs['np'].__version__)
    if 'pd' in globs:
        print("pandas==%s" % globs['pd'].__version__)
    if 'nx' in globs:
        print("networkX==%s" % globs['nx'].__version__)
    if 'scipy' in globs:
        print("scipy==%s" % globs['scipy'].__version__)
    if 'sklearn' in globs:
        print("sklearn==%s" % globs['sklearn'].__version__)
    if 'plt' in globs:
        from matplotlib import __version__ as matplotlib_version
        print("matplotlib==%s" % matplotlib_version)
    if 'sns' in globs:
        print("seaborn==%s" % globs['sns'].__version__)
    if 'gensim' in globs:
        print("Gensim==%s" % globs['gensim'].__version__)
    if 'pyLDAvis' in globs:
        print("pyLDAvis==%s" % globs['pyLDAvis'].__version__)
