import logging
logger = logging.getLogger(__name__)

try:
    from importlib import metadata
except ImportError:
    # Running on pre-3.8 Python; use importlib-metadata package
    import importlib_metadata as metadata

# This is read from package.json in setup.py
# it seems to struggle in dev mode, requiring the try/except below
version = metadata.version('earthscope')

try:
    # e.g. version 1.0.5 => ~1.0
    package_version = "~" + '.'.join(version.split('.')[:-1])
except:
    logger.exception("Couldn't read package_version, returning ~0.2")
    package_version = "~0.2"
