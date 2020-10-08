import sys

if sys.version_info.major == 3:
    from . import check
    from . import detox
else:
    import check
    import detox
