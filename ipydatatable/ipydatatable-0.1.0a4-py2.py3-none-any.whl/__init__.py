from ._version import version_info, __version__

from .ipydatatable import *
import notebook
import os
import shutil


import shutil
import pathlib

from os import listdir
from os.path import isfile, join

path = str(pathlib.Path(__file__).parent.absolute())

static_dir = notebook.DEFAULT_STATIC_FILES_PATH

onlyfiles = [f for f in listdir(static_dir) if isfile(join(static_dir, f))]


files = [ path+'/static/sort_both.png',
            path+'/static/sort_asc.png',
            path+'/static/sort_desc.png',
            path+'/static/sort_desc_disabled.png',
            path+'/static/sort_asc_disabled.png',
        ]

for file in files:
    if file not in onlyfiles:
        shutil.copy2(file, notebook.DEFAULT_STATIC_FILES_PATH)

def _jupyter_nbextension_paths():
    """Called by Jupyter Notebook Server to detect if it is a valid nbextension and
    to install the widget

    Returns
    =======
    section: The section of the Jupyter Notebook Server to change.
        Must be 'notebook' for widget extensions
    src: Source directory name to copy files from. Webpack outputs generated files
        into this directory and Jupyter Notebook copies from this directory during
        widget installation
    dest: Destination directory name to install widget files to. Jupyter Notebook copies
        from `src` directory into <jupyter path>/nbextensions/<dest> directory
        during widget installation
    require: Path to importable AMD Javascript module inside the
        <jupyter path>/nbextensions/<dest> directory
    """
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'ipydatatable',
        'require': 'ipydatatable/extension'
    }]
