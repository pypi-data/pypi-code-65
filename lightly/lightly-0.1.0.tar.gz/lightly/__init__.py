""" Deep Learning Package for Python

Lightly is a Python module for self-supervised active learning.

"""

# Copyright (c) 2020. Lightly AG and its affiliates.
# All Rights Reserved

__name__ = 'lightly'
__version__ = '0.1.0'

try:
    # See (https://github.com/PyTorchLightning/pytorch-lightning)
    # This variable is injected in the __builtins__ by the build
    # process. It used to enable importing subpackages of skimage when
    # the binaries are not built
    __LIGHTLY_SETUP__
except NameError:
    __LIGHTLY_SETUP__ = False


if __LIGHTLY_SETUP__:
    # setting up lightly
    msg = f'Partial import of {__name__}=={__version__} during build process.' 
    print(msg)
else:
    # see if prefetch_generator is available
    try:
        import prefetch_generator
    except ImportError:
        _prefetch_generator_available = False
    else:
        _prefetch_generator_available = True

    # see if sklearn is available
    try:
        import sklearn
    except ImportError:
        _sklearn_available = False
    else:
        _sklearn_available = True


    def is_prefetch_generator_available():
        return _prefetch_generator_available


    def is_sklearn_available():
        return _sklearn_available


    # import core functionalities
    from lightly._core import train_model_and_embed_images
    from lightly._core import train_embedding_model
    from lightly._core import embed_images

    # compare current version v0 to other version v1
    def version_compare(v0, v1):
        v0 = [int(n) for n in v0.split('.')][::-1]
        v1 = [int(n) for n in v1.split('.')][::-1]
        pairs = list(zip(v0, v1))[::-1]
        for x, y in pairs:
            if x < y:
                return -1
            if x > y:
                return 1
        return 0


    # message if current version is not latest version
    def pretty_print_latest_version(latest_version, width=70):
        lines = [
            'There is a newer version of the package available.',
            'For compatability reasons, please upgrade your current version.',
            '> pip install lightly=={}'.format(latest_version),
        ]
        print('-' * width)
        for line in lines:
            print('| ' + line + (width - len(line) - 3) * " " + "|")
        print('-' * width)

    # check for latest version
    from lightly.api import get_latest_version
    latest_version = get_latest_version(__version__)
    if latest_version is not None:
        if version_compare(__version__, latest_version) < 0:
            # local version is behind latest version
            # pretty_print_latest_version(latest_version)
            pass

