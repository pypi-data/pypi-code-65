# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('..'))


# -- Project information -----------------------------------------------------

project = 'objclick'
copyright = '2020, E. Madison Bray'
author = 'E. Madison Bray'

# The full version, including alpha/beta/rc tags
from objclick import __version__ as release


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
        'm2r',
        'sphinx.ext.autodoc',
        'sphinx.ext.intersphinx',
        'sphinx.ext.napoleon'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

default_role = 'py:obj'

# -- Configure extensions- ---------------------------------------------------
## m2r configuration

# the last release of m2r is out of date with current versions of sphinx,
# so for now we monkey-patch it
def _fixup_m2r():
    import m2r
    orig_setup = m2r.setup

    def setup(app):
        app_cls = app.__class__
        try:
            orig_add_source_parser = app_cls.add_source_parser
            app_cls.add_source_parser = app_cls.add_source_suffix
            return orig_setup(app)
        finally:
            app_cls.add_source_parser = orig_add_source_parser

    m2r.setup = setup

_fixup_m2r()


## intersphinx configuration

import click
click_major_version = click.__version__.split('.')[0]
intersphinx_mapping = {
    'click': (f'https://click.palletsprojects.com/en/{click_major_version}.x/',
              None),
    'python': ('https://docs.python.org/3/', None)
}


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_css_files = ['custom.css']
