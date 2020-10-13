import os

import pypigeonhole_build.app_version_control as vc

# ##############################################################################
# This file is used by setup.py for users and the release script for version
# tagging and increment. These code are *not* reusable.
# ##############################################################################

# follow same style, 3 digits, major, minor, patch
# release script is looking for this pattern: app_version =
# so don't use this pattern else where. we should not have 2 assignment
# anyway. Moving this to a text is better, but code is always
# first choice.
__app_version = "0.2.6"

# overwrite default version bumping in app_version_control.bump_version
vc.bump_version = vc.bump_version_upto10


# may change the logic here, e.g., read the version from a text file
# and implement a new version bumping logic.
# tunnel to outside: python setup.py --version
def get_app_version():  # used by setup.py
    return __app_version


# may overwrite these 2 methods, e.g., return constant strings
def get_top_pkg():  # part of conda environment name
    # assume this file's folder is the top package
    # do not go outside of src, since project content is copied to a "work"
    # location during conda packaging, so project folder is not stable.
    # This is not reusable.
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    top_pkg = os.path.basename(curr_dir)
    return top_pkg


# if app name == app directory name == top package name with - to _
# then scripts and python code can ride on this smoothly.
def get_app_name():  # used by setup.py
    top_pkg = get_top_pkg()
    app_name = top_pkg.replace('_', '-')
    return app_name
