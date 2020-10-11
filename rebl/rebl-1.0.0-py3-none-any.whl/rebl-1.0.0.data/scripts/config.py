#!python

# --------------------------------------------------------------------------
# This is a configuration file for rebl, a regular-expression based linter.
# --------------------------------------------------------------------------

import os
import re


# pattern tuples contain
# (description, [match_all_patterns], [match_any_pattern], [match_exclude_pattern])
# if all match patterns are [], a detector function may be invoked for code-based detection.

patterns = {}
patterns[".py"] = {
    "HE0001": (
        "Left behind merge conflict",
        [], ["^<<<<<<< ", "^>>>>>>> "], [],
    ),
    "HW0002": (
        "Best to avoid hasattr, https://hynek.me/articles/hasattr/ - use getattr instead.",
        ['hasattr'], [], [],
    ),
    "HW0003": (
        ".assertEquals is deprecated, use .assertEqual instead.",
        ['\.assertEquals'], [], [],
    ),
}

# Context collectors
# def linehook_py(filename, lines, linenum, context):
#     """
#     Called on every line if defined - permits collecting state data.
#     Keep this as light as possible.
#     State should be kept in dict 'context' which is reset each file.
#     """
#     pass

# Helpers
def absolute_filename(filename):
    return os.path.realpath(os.path.join(os.getcwd(), filename))

# Detectors
# def detect_py_KEYxxxx(filename, line):
#     return True if 'hello' in line else False

# Fixers
def fix_py_HW0003(filename, line):
    return line.replace(".assertEquals", ".assertEqual")
